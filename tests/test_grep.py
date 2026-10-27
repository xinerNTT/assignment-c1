"""Unit tests for logscope.analysers.grep — Phase 4."""

from __future__ import annotations

from datetime import datetime

from logscope.parser import LogEntry, MalformedLine
from logscope.analysers.grep import run

BASE = datetime(2026, 10, 1, 9, 0, 0)
EARLY = datetime(2026, 10, 1, 8, 0, 0)
LATE  = datetime(2026, 10, 1, 10, 0, 0)


def entry(level, ts=BASE, msg="msg"):
    return LogEntry(timestamp=ts, level=level, message=msg, raw=f"{ts} {level} {msg}")

def bad():
    return MalformedLine(raw="bad", line_number=1)


STREAM = [
    entry("INFO",  EARLY, "started"),
    entry("WARN",  BASE,  "high mem"),
    entry("ERROR", BASE,  "disk full"),
    entry("ERROR", LATE,  "timeout"),
    bad(),
]


class TestGrepRun:
    def test_level_filter_error(self):
        r = list(run(iter(STREAM), level="ERROR"))
        assert len(r) == 2
        assert all(e.level == "ERROR" for e in r)

    def test_level_filter_info(self):
        r = list(run(iter(STREAM), level="INFO"))
        assert len(r) == 1 and r[0].message == "started"

    def test_level_case_insensitive(self):
        assert len(list(run(iter(STREAM), level="error"))) == 2

    def test_since_filter(self):
        r = list(run(iter(STREAM), since=BASE))
        assert all(e.timestamp >= BASE for e in r)
        assert not any(e.message == "started" for e in r)

    def test_combined_filters(self):
        r = list(run(iter(STREAM), level="ERROR", since=LATE))
        assert len(r) == 1 and r[0].message == "timeout"

    def test_no_match(self):
        assert list(run(iter(STREAM), level="DEBUG")) == []

    def test_malformed_excluded(self):
        r = list(run(iter(STREAM)))
        assert not any(isinstance(x, MalformedLine) for x in r)

    def test_no_filters_all_valid(self):
        assert len(list(run(iter(STREAM)))) == 4

    def test_since_boundary_inclusive(self):
        assert len(list(run(iter(STREAM), since=EARLY))) == 4
