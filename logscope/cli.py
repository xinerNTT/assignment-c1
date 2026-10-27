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

    result = sa.run(stream_lines(logfile))
    click.echo(tf.format_summary(result))
