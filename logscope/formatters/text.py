"""Plain-text renderers for all logscope commands."""

from __future__ import annotations

from logscope.analysers.summary import SummaryResult

_BAR_CHAR = "#"
_MAX_BAR_WIDTH = 40


def format_summary(result: SummaryResult) -> str:
    lines = ["=" * 50, "  LOG SUMMARY", "=" * 50]
    for level in ("INFO", "WARN", "ERROR", "DEBUG", "CRITICAL"):
        count = result.counts.get(level, 0)
        if count or level in ("INFO", "WARN", "ERROR"):
            lines.append(f"  {level:<10} {count:>8}")
    lines += [
        "",
        f"  Malformed lines : {result.malformed_count}",
        f"  Total lines     : {result.total_lines}",
        "",
    ]
    if result.first_timestamp:
        lines.append(f"  First timestamp : {result.first_timestamp}")
    if result.last_timestamp:
        lines.append(f"  Last timestamp  : {result.last_timestamp}")
    if result.top_errors:
        lines += ["", "  Top ERROR messages:"]
        for i, (msg, cnt) in enumerate(result.top_errors, 1):
            truncated = msg if len(msg) <= 70 else msg[:67] + "..."
            lines.append(f"    {i}. [{cnt:>4}x] {truncated}")
    lines.append("=" * 50)
    return "\n".join(lines)


def format_timeline(buckets: dict[str, int]) -> str:
    if not buckets:
        return "No ERROR entries found in the specified time range."
    max_count = max(buckets.values())
    scale = _MAX_BAR_WIDTH / max_count if max_count else 1
    lines = ["=" * 55, "  ERROR TIMELINE", "=" * 55]
    for label, count in buckets.items():
        bar = _BAR_CHAR * max(1, round(count * scale))
        lines.append(f"  {label} | {bar}  ({count})")
    lines.append("=" * 55)
    return "\n".join(lines)


def format_grep(entries: list) -> str:
    if not entries:
        return "No matching log entries found."
    return "\n".join(e.raw for e in entries)
