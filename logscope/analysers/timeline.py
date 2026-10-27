"""Timeline analyser — ERROR counts bucketed by configurable time window."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Iterator

from logscope.parser import LogEntry, MalformedLine, ParseResult


def parse_bucket_size(bucket_str: str) -> int:
    """Parse '15m', '1h', '30s' → minutes (int)."""
    m = re.fullmatch(r"(\d+)(m|h|s)", bucket_str.strip().lower())
    if m is None:
        raise ValueError(
            f"Invalid bucket size {bucket_str!r}. Use e.g. '15m', '1h', '30s'."
        )
    value, unit = int(m.group(1)), m.group(2)
    if unit == "m":
        return value
    if unit == "h":
        return value * 60
    # seconds — round down to minutes, minimum 1
    return max(1, value // 60)


def floor_to_bucket(ts: datetime, bucket_minutes: int) -> datetime:
    """Floor *ts* to the nearest *bucket_minutes* boundary."""
    total = ts.hour * 60 + ts.minute
    floored = (total // bucket_minutes) * bucket_minutes
    return ts.replace(hour=floored // 60, minute=floored % 60,
                      second=0, microsecond=0)


def run(
    entry_stream: Iterator[ParseResult],
    bucket_minutes: int = 15,
) -> dict[str, int]:
    """Return ordered dict of {HH:MM bucket label: ERROR count}."""
    raw: dict[datetime, int] = {}
    for item in entry_stream:
        if isinstance(item, MalformedLine) or item.level != "ERROR":
            continue
        key = floor_to_bucket(item.timestamp, bucket_minutes)
        raw[key] = raw.get(key, 0) + 1
    return {k.strftime("%H:%M"): v for k, v in sorted(raw.items())}
