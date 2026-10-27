"""Markdown report formatter for all logscope commands."""

from __future__ import annotations

from pathlib import Path

from logscope.analysers.summary import SummaryResult


def _dt(ts) -> str:
    return ts.isoformat() if ts else "N/A"


def _write(path: str, content: str) -> str:
    Path(path).write_text(content, encoding="utf-8")
    return path


def summary_report(r: SummaryResult, output_path: str = "summary_report.md") -> str:
    lines = [
        "# Log Summary Report", "",
        "## Level Counts", "",
        "| Level | Count |", "|-------|------:|",
    ]
    for level in ("INFO", "WARN", "ERROR", "DEBUG", "CRITICAL"):
        count = r.counts.get(level, 0)
        if count or level in ("INFO", "WARN", "ERROR"):
            lines.append(f"| {level} | {count} |")
    lines += [
        "", "## Metadata", "",
        f"- **Total lines**: {r.total_lines}",
        f"- **Malformed lines**: {r.malformed_count}",
        f"- **First timestamp**: {_dt(r.first_timestamp)}",
        f"- **Last timestamp**: {_dt(r.last_timestamp)}",
        "", "## Top Error Messages", "",
        "| # | Message | Count |", "|---|---------|------:|",
    ]
    for i, (msg, cnt) in enumerate(r.top_errors, 1):
        lines.append(f"| {i} | {msg.replace('|', chr(92)+'|')} | {cnt} |")
    return _write(output_path, "\n".join(lines) + "\n")


def timeline_report(buckets: dict[str, int], output_path: str = "timeline_report.md") -> str:
    lines = [
        "# Error Timeline Report", "",
        "| Time Bucket | Error Count |", "|-------------|------------:|",
    ]
    for label, count in buckets.items():
        lines.append(f"| {label} | {count} |")
    return _write(output_path, "\n".join(lines) + "\n")


def grep_report(entries: list, output_path: str = "grep_report.md") -> str:
    lines = [
        "# Log Search Report", "",
        f"**Matches found**: {len(entries)}", "",
        "```",
    ]
    lines += [e.raw for e in entries]
    lines.append("```")
    return _write(output_path, "\n".join(lines) + "\n")
