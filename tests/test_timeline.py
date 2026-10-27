"""Unit tests for logscope.analysers.timeline — Phase 3."""

from __future__ import annotations

from datetime import datetime
import pytest

from logscope.parser import LogEntry, MalformedLine
from logscope.analysers.timeline import run, floor_to_bucket, parse_bucket_size


def entry(level, ts, msg="msg"):
    return LogEntry(timestamp=ts, level=level, message=msg, raw="raw")

def bad():
    return MalformedLine(raw="bad", line_number=1)


class TestParseBucketSize:
    def test_minutes(self):      assert parse_bucket_size("15m") == 15
    def test_hours(self):        assert parse_bucket_size("1h")  == 60
    def test_two_hours(self):    assert parse_bucket_size("2h")  == 120
    def test_seconds_lt60(self): assert parse_bucket_size("30s") == 1
    def test_seconds_gt60(self): assert parse_bucket_size("120s") == 2
    def test_invalid(self):
        with pytest.raises(ValueError): parse_bucket_size("invalid")
    def test_invalid_unit(self):
        with pytest.raises(ValueError): parse_bucket_size("10d")


class TestFloorToBucket:
    def test_on_boundary(self):
        ts = datetime(2026, 10, 1, 8, 0, 0)
        assert floor_to_bucket(ts, 15) == datetime(2026, 10, 1, 8, 0, 0)

    def test_mid_bucket(self):
        ts = datetime(2026, 10, 1, 8, 7, 30)
        assert floor_to_bucket(ts, 15) == datetime(2026, 10, 1, 8, 0, 0)

    def test_last_minute(self):
        ts = datetime(2026, 10, 1, 8, 14, 59)
        assert floor_to_bucket(ts, 15) == datetime(2026, 10, 1, 8, 0, 0)

    def test_next_boundary(self):
        ts = datetime(2026, 10, 1, 8, 15, 0)
        assert floor_to_bucket(ts, 15) == datetime(2026, 10, 1, 8, 15, 0)

    def test_60min_bucket(self):
        ts = datetime(2026, 10, 1, 9, 45, 0)
        assert floor_to_bucket(ts, 60) == datetime(2026, 10, 1, 9, 0, 0)


class TestTimelineRun:
    def test_single_bucket(self):
        stream = [
            entry("ERROR", datetime(2026, 10, 1, 8, 5, 0)),
            entry("ERROR", datetime(2026, 10, 1, 8, 10, 0)),
        ]
        assert run(iter(stream), 15) == {"08:00": 2}

    def test_multiple_buckets(self):
        stream = [
            entry("ERROR", datetime(2026, 10, 1, 8, 5, 0)),
            entry("ERROR", datetime(2026, 10, 1, 8, 20, 0)),
            entry("ERROR", datetime(2026, 10, 1, 8, 35, 0)),
        ]
        b = run(iter(stream), 15)
        assert b == {"08:00": 1, "08:15": 1, "08:30": 1}

    def test_non_error_excluded(self):
        stream = [
            entry("INFO",  datetime(2026, 10, 1, 8, 0, 0)),
            entry("WARN",  datetime(2026, 10, 1, 8, 0, 0)),
            entry("ERROR", datetime(2026, 10, 1, 8, 0, 0)),
        ]
        assert run(iter(stream), 15) == {"08:00": 1}

    def test_malformed_excluded(self):
        stream = [bad(), entry("ERROR", datetime(2026, 10, 1, 8, 0, 0))]
        assert run(iter(stream), 15) == {"08:00": 1}

    def test_empty_log(self):
        assert run(iter([]), 15) == {}

    def test_sorted_chronologically(self):
        stream = [
            entry("ERROR", datetime(2026, 10, 1, 9, 0, 0)),
            entry("ERROR", datetime(2026, 10, 1, 8, 0, 0)),
        ]
        keys = list(run(iter(stream), 15).keys())
        assert keys == sorted(keys)
