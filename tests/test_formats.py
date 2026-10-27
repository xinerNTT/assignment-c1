"""Unit tests for formatters and CLI output formats — Phase 5."""

from __future__ import annotations

import json
import os
import tempfile
import textwrap
from datetime import datetime

import pytest
from click.testing import CliRunner

from logscope.parser import LogEntry
from logscope.analysers.summary import SummaryResult
from logscope.formatters import text as tf
from logscope.formatters import json_fmt
from logscope.formatters import markdown as md
from logscope.cli import main

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SUMMARY = SummaryResult(
    counts={"INFO": 10, "WARN": 3, "ERROR": 5},
    top_errors=[("db timeout", 4), ("disk full", 1)],
    first_timestamp=datetime(2026, 10, 1, 8, 0, 0),
    last_timestamp=datetime(2026, 10, 1, 17, 0, 0),
    malformed_count=2,
    total_lines=20,
)
BUCKETS = {"08:00": 3, "08:15": 6, "08:30": 2}
ENTRIES = [
    LogEntry(datetime(2026, 10, 1, 8, 0, 0), "ERROR", "disk full",
             "2026-10-01 08:00:00 ERROR disk full"),
    LogEntry(datetime(2026, 10, 1, 8, 1, 0), "WARN", "high mem",
             "2026-10-01 08:01:00 WARN  high mem"),
]

SAMPLE_LOG = textwrap.dedent("""\
    2026-10-01 08:00:00 INFO  App started
    2026-10-01 08:00:01 WARN  Low memory
    2026-10-01 08:00:02 ERROR Disk full
    2026-10-01 08:00:03 ERROR Disk full
    2026-10-01 08:15:10 ERROR Timeout connecting to DB
    this line is malformed
    2026-10-01 09:00:00 INFO  App recovered
""")


@pytest.fixture()
def logfile(tmp_path):
    p = tmp_path / "test.log"
    p.write_text(SAMPLE_LOG, encoding="utf-8")
    return str(p)


@pytest.fixture()
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# Text formatter
# ---------------------------------------------------------------------------

class TestTextFormatter:
    def test_summary_level_counts(self):
        out = tf.format_summary(SUMMARY)
        assert "INFO" in out and "10" in out

    def test_summary_top_errors(self):
        assert "db timeout" in tf.format_summary(SUMMARY)

    def test_timeline_bar_chart(self):
        out = tf.format_timeline(BUCKETS)
        assert "08:00" in out and "#" in out

    def test_timeline_empty(self):
        assert "No ERROR" in tf.format_timeline({})

    def test_grep_raw_lines(self):
        out = tf.format_grep(ENTRIES)
        assert "disk full" in out and "high mem" in out

    def test_grep_empty(self):
        assert "No matching" in tf.format_grep([])


# ---------------------------------------------------------------------------
# JSON formatter
# ---------------------------------------------------------------------------

class TestJsonFormatter:
    def test_summary_round_trip(self):
        d = json.loads(json_fmt.to_json(json_fmt.summary_to_dict(SUMMARY)))
        assert d["counts"]["INFO"] == 10
        assert d["malformed_count"] == 2
        assert d["top_errors"][0]["message"] == "db timeout"

    def test_timeline_round_trip(self):
        d = json.loads(json_fmt.to_json(json_fmt.timeline_to_dict(BUCKETS)))
        assert d["buckets"][0] == {"time": "08:00", "error_count": 3}

    def test_grep_round_trip(self):
        d = json.loads(json_fmt.to_json(json_fmt.grep_to_dict(ENTRIES)))
        assert d["count"] == 2
        assert d["entries"][0]["level"] == "ERROR"


# ---------------------------------------------------------------------------
# Markdown formatter
# ---------------------------------------------------------------------------

class TestMarkdownFormatter:
    def test_summary_report(self, tmp_path):
        p = str(tmp_path / "s.md")
        md.summary_report(SUMMARY, output_path=p)
        content = open(p).read()
        assert "# Log Summary Report" in content
        assert "db timeout" in content

    def test_timeline_report(self, tmp_path):
        p = str(tmp_path / "t.md")
        md.timeline_report(BUCKETS, output_path=p)
        assert "08:15" in open(p).read()

    def test_grep_report(self, tmp_path):
        p = str(tmp_path / "g.md")
        md.grep_report(ENTRIES, output_path=p)
        assert "disk full" in open(p).read()


# ---------------------------------------------------------------------------
# CLI --format flag integration
# ---------------------------------------------------------------------------

class TestCLIFormats:
    def test_summary_json(self, runner, logfile):
        r = runner.invoke(main, ["summary", logfile, "--format", "json"])
        assert r.exit_code == 0
        d = json.loads(r.output)
        assert d["counts"]["ERROR"] == 3
        assert d["malformed_count"] == 1

    def test_summary_md(self, runner, logfile, tmp_path):
        with runner.isolated_filesystem(temp_dir=tmp_path):
            r = runner.invoke(main, ["summary", logfile, "--format", "md"])
        assert r.exit_code == 0
        assert "Report written" in r.output

    def test_timeline_json(self, runner, logfile):
        r = runner.invoke(main, ["timeline", logfile, "--bucket", "15m",
                                  "--format", "json"])
        assert r.exit_code == 0
        d = json.loads(r.output)
        total = sum(b["error_count"] for b in d["buckets"])
        assert total == 3

    def test_timeline_md(self, runner, logfile, tmp_path):
        with runner.isolated_filesystem(temp_dir=tmp_path):
            r = runner.invoke(main, ["timeline", logfile, "--format", "md"])
        assert r.exit_code == 0

    def test_grep_json(self, runner, logfile):
        r = runner.invoke(main, ["grep", logfile, "--level", "ERROR",
                                  "--format", "json"])
        assert r.exit_code == 0
        d = json.loads(r.output)
        assert d["count"] == 3

    def test_grep_md(self, runner, logfile, tmp_path):
        with runner.isolated_filesystem(temp_dir=tmp_path):
            r = runner.invoke(main, ["grep", logfile, "--level", "ERROR",
                                      "--format", "md"])
        assert r.exit_code == 0

    def test_invalid_bucket(self, runner, logfile):
        r = runner.invoke(main, ["timeline", logfile, "--bucket", "bad"])
        assert r.exit_code != 0

    def test_invalid_since(self, runner, logfile):
        r = runner.invoke(main, ["grep", logfile, "--since", "not-a-date"])
        assert r.exit_code != 0
