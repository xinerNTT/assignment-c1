"""Streaming log parser for logscope.

Reads a log file line-by-line without loading the entire file into memory.
Each line is parsed into a LogEntry on success or a MalformedLine on failure.

Expected log format (from SPEC.md):
    YYYY-MM-DD HH:MM:SS[.ffffff] LEVEL message...

Example:
    2026-10-01 08:23:11 ERROR Failed to connect to DB: timeout
    2026-10-01 08:23:12 INFO  Request received

Performance notes:
    - Timestamp is parsed with manual integer slicing (no strptime) for speed.
    - Regex is pre-compiled at module load and reused across all lines.
    - File is opened with a 64 KB read buffer to reduce syscall count.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Union

# ---------------------------------------------------------------------------
# Log line pattern
# ---------------------------------------------------------------------------
_LOG_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?)"
    r"[ \t]+"
    r"(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL)"
    r"[ \t]+"
    r"(.+)$",
    re.IGNORECASE,
)

# Normalisation: WARNING → WARN, FATAL → ERROR
_LEVEL_MAP: dict[str, str] = {
    "DEBUG": "DEBUG",
    "INFO": "INFO",
    "WARN": "WARN",
    "WARNING": "WARN",
    "ERROR": "ERROR",
    "CRITICAL": "CRITICAL",
    "FATAL": "ERROR",
}

VALID_LEVELS = frozenset(_LEVEL_MAP.values())


@dataclass(slots=True)
class LogEntry:
    """A successfully parsed log line."""
    timestamp: datetime
    level: str
    message: str
    raw: str


@dataclass(slots=True)
class MalformedLine:
    """A line that could not be parsed."""
    raw: str
    line_number: int


ParseResult = Union[LogEntry, MalformedLine]


def stream_lines(path: str) -> Iterator[ParseResult]:
    """Yield LogEntry or MalformedLine for every line in *path*.

    The file is read line-by-line — the entire file is never loaded into memory.
    The function never raises on bad input; malformed lines are yielded as
    MalformedLine objects.

    Args:
        path: Filesystem path to the log file.

    Yields:
        LogEntry for well-formed lines, MalformedLine otherwise.
    """
    _match = _LOG_RE.match
    _level_map = _LEVEL_MAP
    _fast_ts = _parse_timestamp_fast

    with open(path, "r", encoding="utf-8", errors="replace", buffering=65536) as fh:
        for line_number, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n\r")
            if not line:
                yield MalformedLine(raw=line, line_number=line_number)
                continue

            m = _match(line)
            if m is None:
                yield MalformedLine(raw=line, line_number=line_number)
                continue

            ts_str, level_raw, message = m.group(1), m.group(2), m.group(3)
            level = _level_map.get(level_raw.upper())
            if level is None:
                yield MalformedLine(raw=line, line_number=line_number)
                continue

            ts = _fast_ts(ts_str)
            if ts is None:
                yield MalformedLine(raw=line, line_number=line_number)
                continue

            yield LogEntry(timestamp=ts, level=level, message=message, raw=line)


def _parse_timestamp_fast(ts_str: str) -> datetime | None:
    """Parse a fixed-width ISO-8601-ish timestamp using integer slicing.

    Returns None on any parse error so the hot loop avoids try/except overhead.
    Supports YYYY-MM-DD HH:MM:SS[.ffffff] and YYYY-MM-DDTHH:MM:SS[.ffffff].
    """
    try:
        year   = int(ts_str[0:4])
        month  = int(ts_str[5:7])
        day    = int(ts_str[8:10])
        hour   = int(ts_str[11:13])
        minute = int(ts_str[14:16])
        second = int(ts_str[17:19])
        micro  = 0
        if len(ts_str) > 19 and ts_str[19] == ".":
            frac = ts_str[20:]
            micro = int(frac[:6].ljust(6, "0"))
        return datetime(year, month, day, hour, minute, second, micro)
    except (ValueError, IndexError):
        return None


def _parse_line(line: str, line_number: int) -> ParseResult:
    """Parse a single line (public helper used by tests)."""
    if not line.strip():
        return MalformedLine(raw=line, line_number=line_number)
    m = _LOG_RE.match(line)
    if m is None:
        return MalformedLine(raw=line, line_number=line_number)
    ts_str, level_raw, message = m.group(1), m.group(2), m.group(3)
    level = _LEVEL_MAP.get(level_raw.upper())
    if level is None:
        return MalformedLine(raw=line, line_number=line_number)
    ts = _parse_timestamp_fast(ts_str)
    if ts is None:
        return MalformedLine(raw=line, line_number=line_number)
    return LogEntry(timestamp=ts, level=level, message=message, raw=line)
