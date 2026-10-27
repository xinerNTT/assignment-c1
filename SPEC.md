# LogScope Specification

## Purpose

LogScope is a command-line tool for quickly analysing application logs after an incident.

The tool is intended for operations and support teams who need a lightweight way to inspect logs without opening a monitoring dashboard.

The solution must be robust, memory-efficient, and capable of processing large log files.

---

# Supported Commands

## Summary

### Usage

```bash
logscope summary app.log
```

### Description

Produces a high-level summary of a log file.

### Output

- INFO count
- WARN count
- ERROR count
- Top 5 most frequent error messages
- First timestamp found
- Last timestamp found
- Malformed line count

### Example

```text
INFO: 1234
WARN: 56
ERROR: 78

Top Errors:
1. Database connection timeout (24)
2. Payment service unavailable (18)
3. Disk space critically low (11)

First Timestamp: 2026-10-01 08:00:01
Last Timestamp: 2026-10-01 18:42:19

Malformed Lines: 3
```

---

## Timeline

### Usage

```bash
logscope timeline app.log --bucket 15m
```

### Description

Displays ERROR occurrences grouped into time buckets.

### Parameters

```text
--bucket
```

Supported examples:

```text
1m
5m
15m
30m
1h
```

### Example Output

```text
09:00 | ###
09:15 | ######
09:30 | ##
09:45 | ####
```

Where:

```text
# = one or more errors
```

---

## Grep

### Usage

```bash
logscope grep app.log --level ERROR
```

or

```bash
logscope grep app.log \
  --level ERROR \
  --since "2026-10-01 09:00"
```

### Description

Filters log entries.

### Supported Filters

#### Level

```bash
--level INFO
--level WARN
--level ERROR
```

#### Since Timestamp

```bash
--since "YYYY-MM-DD HH:MM"
```

Returns entries occurring on or after the supplied timestamp.

### Example Output

```text
2026-10-01 09:01:18 ERROR Payment service unavailable
2026-10-01 09:05:15 ERROR Database connection timeout
2026-10-01 09:08:33 ERROR Disk space critically low
```

---

# Output Formats

Every command must support:

```bash
--format json
```

and

```bash
--format md
```

Default output format:

```text
text
```

---

## JSON Output

Example:

```bash
logscope summary app.log --format json
```

```json
{
  "info": 120,
  "warn": 15,
  "error": 8,
  "first_timestamp": "2026-10-01 08:00:00",
  "last_timestamp": "2026-10-01 10:25:13",
  "malformed_lines": 1
}
```

---

## Markdown Output

Example:

```bash
logscope summary app.log --format md
```

Creates:

```text
summary_report.md
```

Example:

```md
# Log Summary

- INFO: 120
- WARN: 15
- ERROR: 8

## Top Errors

1. Database connection timeout (4)
2. Payment service unavailable (2)

## Time Range

First Timestamp: 2026-10-01 08:00:00

Last Timestamp: 2026-10-01 10:25:13

## Malformed Lines

1
```

Markdown report filenames:

```text
summary_report.md
timeline_report.md
grep_report.md
```

---

# Log Format

Expected input format:

```text
YYYY-MM-DD HH:MM:SS LEVEL MESSAGE
```

Example:

```text
2026-10-01 09:00:00 INFO Application started
2026-10-01 09:01:03 WARN Cache nearing limit
2026-10-01 09:02:15 ERROR Database connection timeout
```

Supported levels:

```text
INFO
WARN
ERROR
```

---

# Parser Behaviour

The parser must process logs line-by-line.

Valid lines are converted into:

```text
timestamp
level
message
```

Malformed lines must:

- be counted
- be skipped
- never terminate processing
- never crash the application

Example malformed lines:

```text
INVALID ENTRY
2026-10-01 ERROR Missing timestamp
abc123
```

---

# Performance Requirements

The tool must handle:

```text
100 MB log files
```

without loading the entire file into memory.

Required approach:

```text
stream processing
```

Examples:

Python:

```python
for line in file:
```

Node.js:

```javascript
readline.createInterface(...)
```

The following approaches are prohibited:

```python
file.read()
file.readlines()
```

or any equivalent whole-file loading mechanism.

---

# Error Handling

The tool must:

- continue processing when malformed lines are encountered
- report malformed line count
- provide clear error messages for invalid arguments
- return non-zero exit codes for command failures

The tool must never crash because of malformed log contents.

---

# Testing Requirements

Unit tests must be implemented for:

## Parser

- valid line
- malformed line
- empty line
- invalid timestamp
- unsupported log format

## Summary

- level counts
- top 5 errors
- timestamp range
- malformed count

## Timeline

- bucket creation
- bucket aggregation
- empty logs

## Grep

- level filter
- since filter
- combined filters

All tests must pass.

---

# Acceptance Criteria

- [ ] summary command works
- [ ] timeline command works
- [ ] grep command works
- [ ] json output supported
- [ ] markdown output supported
- [ ] malformed lines counted
- [ ] malformed lines skipped
- [ ] parser tests passing
- [ ] command tests passing
- [ ] processes 100 MB file successfully
- [ ] does not load entire file into memory
- [ ] memory remains stable during execution

---

# Non-Functional Requirements

- Python or Node.js
- Modular code structure
- Command-line interface
- Deterministic test suite
- Clear error messages
- Suitable for Linux, macOS and Windows environments