"""JSON formatter for all logscope commands."""

from __future__ import annotations

import json
from typing import Any

from logscope.analysers.summary import SummaryResult


def _dt(ts) -> str | None:
    return ts.isoformat() if ts else None


def summary_to_dict(r: SummaryResult) -> dict[str, Any]:
    return {
        "counts": r.counts,
        "top_errors": [{"message": m, "count": c} for m, c in r.top_errors],
        "first_timestamp": _dt(r.first_timestamp),
        "last_timestamp": _dt(r.last_timestamp),
        "malformed_count": r.malformed_count,
        "total_lines": r.total_lines,
    }


def timeline_to_dict(buckets: dict[str, int]) -> dict[str, Any]:
    return {"buckets": [{"time": k, "error_count": v} for k, v in buckets.items()]}


def grep_to_dict(entries: list) -> dict[str, Any]:
    return {
        "count": len(entries),
        "entries": [
            {"timestamp": _dt(e.timestamp), "level": e.level, "message": e.message}
            for e in entries
        ],
    }


def to_json(data: dict[str, Any], indent: int = 2) -> str:
    return json.dumps(data, indent=indent, default=str)
