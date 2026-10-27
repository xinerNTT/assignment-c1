"""Unit tests for logscope.analysers.summary — Phase 2."""

from __future__ import annotations

from datetime import datetime
import pytest

from logscope.parser import LogEntry, MalformedLine
from logscope.analysers.summary import run


def entry(level, msg="msg", ts=datetime(2026, 10, 1, 8, 0, 0)):
    return LogEntry(timestamp=ts, level=level, message=msg, raw="raw")

def bad(n=1):
    return MalformedLine(raw="bad", line_number=n)


class TestSummaryRun:
    def test_counts_by_level(self):
        r = run(iter([entry("INFO"), entry("INFO"), entry("WARN"), entry("ERROR")]))
        assert r.counts["INFO"] == 2
        assert r.counts["WARN"] == 1
        assert r.counts["ERROR"] == 1

    def test_malformed_line_count(self):
        r = run(iter([entry("INFO"), bad(1), bad(2)]))
        assert r.malformed_count == 2
        assert r.total_lines == 3

    def test_top_errors(self):
        errors = [
            entry("ERROR", "db timeout"), entry("ERROR", "db timeout"),
            entry("ERROR", "disk full"),  entry("ERROR", "db timeout"),
            entry("ERROR", "oom"),
        ]
        r = run(iter(errors), top_n=2)
        assert r.top_errors[0] == ("db timeout", 3)

    def test_top_errors_respects_top_n(self):
        r = run(iter([entry("ERROR", f"e{i}") for i in range(10)]), top_n=3)
        assert len(r.top_errors) == 3

    def test_timestamp_range(self):
        early = datetime(2026, 10, 1, 8, 0, 0)
        late  = datetime(2026, 10, 1, 12, 0, 0)
        r = run(iter([entry("INFO", ts=late), entry("INFO", ts=early)]))
        assert r.first_timestamp == early
        assert r.last_timestamp  == late

    def test_empty_stream(self):
        r = run(iter([]))
        assert r.counts == {}
        assert r.top_errors == []
        assert r.first_timestamp is None
        assert r.malformed_count == 0

    def test_only_malformed(self):
        r = run(iter([bad(i) for i in range(5)]))
        assert r.malformed_count == 5
        assert r.counts == {}
        assert r.first_timestamp is None
