"""Unit tests for logscope.parser — Phase 1."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime

from logscope.parser import LogEntry, MalformedLine, _parse_line, stream_lines


def parse(line: str, n: int = 1):
    return _parse_line(line, n)


class TestParseLine:
    def test_valid_line(self):
        r = parse("2026-10-01 08:23:11 ERROR Failed to connect to DB")
        assert isinstance(r, LogEntry)
        assert r.level == "ERROR"
        assert r.message == "Failed to connect to DB"
        assert r.timestamp == datetime(2026, 10, 1, 8, 23, 11)

    def test_valid_info(self):
        r = parse("2026-10-01 09:00:00 INFO  Server started")
        assert isinstance(r, LogEntry)
        assert r.level == "INFO"

    def test_valid_warn(self):
        r = parse("2026-10-01 09:00:01 WARN  Disk usage high")
        assert isinstance(r, LogEntry)
        assert r.level == "WARN"

    def test_warning_normalised_to_warn(self):
        r = parse("2026-10-01 09:00:02 WARNING Disk usage high")
        assert isinstance(r, LogEntry)
        assert r.level == "WARN"

    def test_fatal_normalised_to_error(self):
        r = parse("2026-10-01 09:00:03 FATAL  Process killed")
        assert isinstance(r, LogEntry)
        assert r.level == "ERROR"

    def test_timestamp_with_microseconds(self):
        r = parse("2026-10-01 08:23:11.123456 INFO  msg")
        assert isinstance(r, LogEntry)
        assert r.timestamp.microsecond == 123456

    def test_t_separator(self):
        r = parse("2026-10-01T08:23:11 INFO  msg")
        assert isinstance(r, LogEntry)

    def test_malformed_no_level(self):
        r = parse("2026-10-01 08:23:11 this is not a level line", 5)
        assert isinstance(r, MalformedLine)
        assert r.line_number == 5

    def test_malformed_invalid_timestamp(self):
        r = parse("not-a-date ERROR something", 3)
        assert isinstance(r, MalformedLine)

    def test_malformed_bad_month(self):
        r = parse("2026-99-01 08:23:11 ERROR msg", 2)
        assert isinstance(r, MalformedLine)

    def test_missing_level_field(self):
        r = parse("2026-10-01 08:23:11", 7)
        assert isinstance(r, MalformedLine)

    def test_empty_line(self):
        r = parse("", 10)
        assert isinstance(r, MalformedLine)

    def test_whitespace_only(self):
        r = parse("   ", 11)
        assert isinstance(r, MalformedLine)

    def test_raw_preserved_entry(self):
        raw = "2026-10-01 08:23:11 ERROR some message"
        r = parse(raw)
        assert isinstance(r, LogEntry)
        assert r.raw == raw

    def test_raw_preserved_malformed(self):
        raw = "this is junk"
        r = parse(raw, 4)
        assert isinstance(r, MalformedLine)
        assert r.raw == raw


class TestStreamLines:
    LOG = (
        "2026-10-01 08:00:00 INFO  App started\n"
        "2026-10-01 08:00:01 WARN  Low memory\n"
        "2026-10-01 08:00:02 ERROR Disk full\n"
        "this line is malformed\n"
        "\n"
        "2026-10-01 08:00:04 INFO  Recovered\n"
    )

    def _stream(self, content: str):
        fd, path = tempfile.mkstemp(suffix=".log")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return list(stream_lines(path))
        finally:
            os.unlink(path)

    def test_correct_entry_and_malformed_counts(self):
        results = self._stream(self.LOG)
        entries = [r for r in results if isinstance(r, LogEntry)]
        bad = [r for r in results if isinstance(r, MalformedLine)]
        assert len(entries) == 4
        assert len(bad) == 2

    def test_never_raises_on_garbage(self):
        results = self._stream("!!!\x00binary\nno log here\n")
        assert all(isinstance(r, MalformedLine) for r in results)

    def test_order_preserved(self):
        results = self._stream(self.LOG)
        levels = [r.level for r in results if isinstance(r, LogEntry)]
        assert levels == ["INFO", "WARN", "ERROR", "INFO"]
