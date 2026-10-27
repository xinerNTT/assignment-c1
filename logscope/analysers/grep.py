"""Grep analyser — filters log entries by level and/or since timestamp."""

from __future__ import annotations

from datetime import datetime
from typing import Iterator, Optional

from logscope.parser import LogEntry, MalformedLine, ParseResult


def run(
    entry_stream: Iterator[ParseResult],
    level: Optional[str] = None,
    since: Optional[datetime] = None,
) -> Iterator[LogEntry]:
    """Yield LogEntry items matching all active filters (streaming)."""
    level_upper = level.upper() if level else None
    for item in entry_stream:
        if isinstance(item, MalformedLine):
            continue
        if level_upper and item.level != level_upper:
            continue
        if since and item.timestamp < since:
            continue
        yield item
