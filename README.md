# LogScope

LogScope is a command-line log analysis tool that processes application logs efficiently, including large log files (100 MB+), without loading the entire file into memory.

## Features

- Summary statistics for log files
  - INFO / WARN / ERROR counts
  - Top 5 error messages
  - First and last timestamps
- Timeline analysis
  - Error counts grouped into configurable time buckets
  - Text-based bar chart output
- Log filtering (grep)
  - Filter by log level
  - Filter by timestamp
- Multiple output formats
  - Text
  - JSON
  - Markdown report
- Streaming log processing
  - Handles large log files efficiently
- Fault-tolerant parsing
  - Malformed lines are counted and skipped
  - Invalid entries never crash the application

---

## Installation

### Clone the repository

```bash
git clone <repository-url>
cd assignment-c1
```

### Install dependencies

```bash
pip install -e .
```

If using Ubuntu/WSL:

```bash
python3 -m pip install -e . 
```

---

## Log Format

The tool expects log lines in the following format:

```text
2026-10-01 09:00:00 INFO Application started
2026-10-01 09:01:15 WARN Database connection slow
2026-10-01 09:02:30 ERROR Failed to connect to database
```

Malformed lines are ignored and counted.

---

## Usage

### Summary

Displays log counts, error statistics, and timestamp range.

```bash
python3 -m logscope.cli summary sample.log
```

Example:

```text
INFO: 120
WARN: 15
ERROR: 5

Top Errors:
1. Database timeout (3)
2. Connection failed (2)

First Timestamp:
2026-10-01 09:00:00

Last Timestamp:
2026-10-01 12:45:00
```

---

### Timeline

Displays ERROR counts grouped by a time bucket.

```bash
python3 -m logscope.cli timeline sample.log --bucket 15m
```

Example:

```text
09:00 #### 4
09:15 ## 2
09:30 ##### 5
```

Supported bucket examples:

```bash
--bucket 5m
--bucket 15m
--bucket 30m
--bucket 60m
```

---

### Grep

Filter log entries by level.

```bash
python3 -m logscope.cli grep sample.log --level ERROR
```

Filter by timestamp:

```bash
python3 -m logscope.cli grep sample.log \
  --level ERROR \
  --since "2026-10-01 09:00"
```

---

## Output Formats

All commands support:

```bash
--format text
--format json
--format md
```

### JSON Output

```bash
python3 -m logscope.cli summary sample.log --format json
```

Example:

```json
{
  "info": 120,
  "warn": 15,
  "error": 5
}
```

### Markdown Report

```bash
python3 -m logscope.cli summary sample.log --format md
```

Example output:

```text
Report written to summary_report.md
```

---

## Architecture

```text
logscope/
├── analysers/
│   ├── summary.py
│   ├── timeline.py
│   └── grep.py
│
├── formatters/
│   ├── text.py
│   ├── json_fmt.py
│   └── markdown.py
│
├── parser.py
├── cli.py
└── __init__.py
```

### Components

#### Parser

Streams log lines one at a time and converts valid entries into structured objects.

#### Analysers

Business logic for:

- Summary generation
- Timeline generation
- Log filtering

#### Formatters

Responsible for rendering outputs as:

- Text
- JSON
- Markdown

#### CLI

Provides user-facing commands using Click.

---

## Memory Efficiency

LogScope processes files using streaming:

```python
with open(path, "r") as log_file:
    for line in log_file:
        ...
```

This approach avoids loading the entire log into memory and allows efficient processing of large log files (100 MB+).

---

## Error Handling

Malformed log lines:

```text
INVALID LINE
```

are:

- Counted
- Skipped
- Never cause the application to crash

---

## Running Tests

Run all tests:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run a specific test:

```bash
pytest tests/test_formats.py -v
```

---

## Future Improvements

- CSV export
- Regex-based grep
- Colored terminal output
- Real-time log tailing
- Interactive dashboard

---
