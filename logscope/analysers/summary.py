"""Summary analyser — single-pass level counts, top errors, timestamp range."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator, Optional

from logscope.parser import LogEntry, MalformedLine, ParseResult


@dataclass
class SummaryResult:
    counts: dict[str, int] = field(default_factory=dict)
    top_errors: list[tuple[str, int]] = field(default_factory=list)
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    malformed_count: int = 0
    total_lines: int = 0


def run(entry_stream: Iterator[ParseResult], top_n: int = 5) -> SummaryResult:
    """Consume *entry_stream* in a single pass and return a SummaryResult."""
    level_counts: Counter[str] = Counter()
    error_counter: Counter[str] = Counter()
    first_ts: Optional[datetime] = None
    last_ts: Optional[datetime] = None
    malformed = 0
    total = 0

    for item in entry_stream:
        total += 1
        if isinstance(item, MalformedLine):
            malformed += 1
            continue
        entry: LogEntry = item
        level_counts[entry.level] += 1
        if entry.level == "ERROR":
            error_counter[entry.message] += 1
        if first_ts is None or entry.timestamp < first_ts:
            first_ts = entry.timestamp
        if last_ts is None or entry.timestamp > last_ts:
            last_ts = entry.timestamp

    return SummaryResult(
        counts=dict(level_counts),
        top_errors=error_counter.most_common(top_n),
        first_timestamp=first_ts,
        last_timestamp=last_ts,
        malformed_count=malformed,
        total_lines=total,
    )
