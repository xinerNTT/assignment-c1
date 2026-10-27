"""logscope CLI — commands added incrementally per phase."""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Optional

import click

from logscope.parser import stream_lines

_FORMAT_CHOICES = click.Choice(["text", "json", "md"], case_sensitive=False)


def _abort(msg: str) -> None:
    click.echo(f"Error: {msg}", err=True)
    sys.exit(1)


@click.group()
def main() -> None:
    """logscope – summarize and analyze application logs."""


# ---------------------------------------------------------------------------
# Phase 2 – summary
# ---------------------------------------------------------------------------

@main.command("summary")
@click.argument("logfile", type=click.Path(exists=True, readable=True))
@click.option("--format", "fmt", default="text", type=_FORMAT_CHOICES)
def summary_cmd(logfile: str, fmt: str) -> None:
    """Show counts, top errors and timestamp range for LOGFILE."""
    from logscope.analysers import summary as sa
    from logscope.formatters import text as tf
    from logscope.formatters import json_fmt
    from logscope.formatters import markdown as md

    result = sa.run(stream_lines(logfile))
    if fmt == "json":
        click.echo(json_fmt.to_json(json_fmt.summary_to_dict(result)))
    elif fmt == "md":
        path = md.summary_report(result)
        click.echo(f"Report written to {path}")
    else:
        click.echo(tf.format_summary(result))


# ---------------------------------------------------------------------------
# Phase 3 – timeline
# ---------------------------------------------------------------------------

@main.command("timeline")
@click.argument("logfile", type=click.Path(exists=True, readable=True))
@click.option("--bucket", "bucket_str", default="15m", show_default=True)
@click.option("--format", "fmt", default="text", type=_FORMAT_CHOICES)
def timeline_cmd(logfile: str, bucket_str: str, fmt: str) -> None:
    """Show ERROR counts grouped by time bucket for LOGFILE."""
    from logscope.analysers import timeline as tla
    from logscope.formatters import text as tf
    from logscope.formatters import json_fmt
    from logscope.formatters import markdown as md

    try:
        bucket_minutes = tla.parse_bucket_size(bucket_str)
    except ValueError as exc:
        _abort(str(exc))

    buckets = tla.run(stream_lines(logfile), bucket_minutes=bucket_minutes)
    if fmt == "json":
        click.echo(json_fmt.to_json(json_fmt.timeline_to_dict(buckets)))
    elif fmt == "md":
        path = md.timeline_report(buckets)
        click.echo(f"Report written to {path}")
    else:
        click.echo(tf.format_timeline(buckets))


# ---------------------------------------------------------------------------
# Phase 4 – grep
# ---------------------------------------------------------------------------

_SINCE_FMTS = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]


def _parse_since(s: str) -> datetime:
    for fmt in _SINCE_FMTS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse --since {s!r}. Use 'YYYY-MM-DD HH:MM:SS'.")


@main.command("grep")
@click.argument("logfile", type=click.Path(exists=True, readable=True))
@click.option("--level", default=None)
@click.option("--since", "since_str", default=None)
@click.option("--format", "fmt", default="text", type=_FORMAT_CHOICES)
def grep_cmd(logfile: str, level: Optional[str], since_str: Optional[str], fmt: str) -> None:
    """Filter and display log entries from LOGFILE."""
    from logscope.analysers import grep as ga
    from logscope.formatters import text as tf
    from logscope.formatters import json_fmt
    from logscope.formatters import markdown as md

    since: Optional[datetime] = None
    if since_str:
        try:
            since = _parse_since(since_str)
        except ValueError as exc:
            _abort(str(exc))

    entries = list(ga.run(stream_lines(logfile), level=level, since=since))
    if fmt == "json":
        click.echo(json_fmt.to_json(json_fmt.grep_to_dict(entries)))
    elif fmt == "md":
        path = md.grep_report(entries)
        click.echo(f"Report written to {path}")
    else:
        click.echo(tf.format_grep(entries))

if __name__ == "__main__":
    main()
