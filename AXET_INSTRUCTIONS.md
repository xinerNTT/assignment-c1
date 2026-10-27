# AXET CODE PROJECT INSTRUCTIONS

## Project
Build a CLI application called `logscope` that summarizes and analyzes application logs.

Language: Python (preferred) or Node.js

---

# Development Rules

## 1. Plan Before Coding

DO NOT write any code immediately.

First, read `SPEC.md` and produce:

1. Architecture overview
2. Data flow
3. Log format assumptions
4. Module structure
5. Test strategy
6. Performance strategy for 100 MB logs
7. Step-by-step implementation plan

Wait for review and approval before generating any code.

The git history must clearly show:
- specification
- planning
- implementation

not a single large commit.

---

# 2. Build Incrementally

Implement in the following order only:

## Step 1 - Parser

Deliver:

- streaming log reader
- log line parser
- malformed line handling
- parser unit tests

Requirements:

- process file line-by-line
- never load entire file into memory
- malformed lines must be counted and skipped
- parser must never crash on bad input

Run tests.

Commit:

```text
feat(parser): add streaming log parser
```

---

## Step 2 - Summary Command

Implement:

```bash
logscope summary app.log
```

Features:

- INFO count
- WARN count
- ERROR count
- top 5 error messages
- first timestamp
- last timestamp
- malformed line count

Run tests.

Commit:

```text
feat(summary): add log summary command
```

---

## Step 3 - Timeline Command

Implement:

```bash
logscope timeline app.log --bucket 15m
```

Features:

- error count grouped by bucket
- text-based bar chart
- configurable bucket size

Example:

08:00 | ###
08:15 | ######
08:30 | ##

Run tests.

Commit:

```text
feat(timeline): add error timeline analysis
```

---

## Step 4 - Grep Command

Implement:

```bash
logscope grep app.log --level ERROR
```

Support:

```bash
--level
--since
```

Examples:

```bash
logscope grep app.log --level WARN

logscope grep app.log \
  --level ERROR \
  --since "2026-10-01 09:00"
```

Run tests.

Commit:

```text
feat(grep): add filtered log search
```

---

## Step 5 - Output Formats

Implement for every command:

```bash
--format json
--format md
```

Requirements:

### json

Print structured JSON.

### md

Generate a markdown report file.

Example:

summary_report.md

timeline_report.md

grep_report.md

Run tests.

Commit:

```text
feat(output): add json and markdown formats
```

---

# 3. Testing Requirements

Create unit tests for:

## Parser

- valid line
- malformed line
- invalid timestamp
- missing level
- empty line

## Summary

- counts by level
- top errors
- timestamp range
- malformed line count

## Timeline

- bucket grouping
- multiple buckets
- empty logs

## Grep

- level filtering
- since filtering
- combined filters

---

# 4. Performance Requirements

The solution MUST handle a 100 MB log.

Requirements:

- stream processing only
- stable memory usage
- no read-all operations
- no loading entire file into arrays/lists

Avoid:

- read()
- readFile()
- splitlines()
- collecting entire file before processing

Preferred:

Python:
```python
for line in file:
```

Node.js:
```js
readline.createInterface(...)
```

---

# 5. Synthetic Log Generator

Create:

```text
scripts/gen_log
```

Purpose:

Generate realistic synthetic logs.

Parameters:

```bash
scripts/gen_log --size 100MB
```

Include:

- INFO
- WARN
- ERROR
- repeated errors
- malformed lines

Output:

```text
sample_100mb.log
```

---

# 6. Benchmarking

After implementation:

Measure:

- runtime
- peak memory usage

Commands:

```bash
time logscope summary sample_100mb.log
```

or platform equivalent.

Provide benchmark results.

Acceptance target:

- 100 MB log processed under 60 seconds
- memory remains stable

---

# 7. Stretch Goal

Optional command:

```bash
logscope explain app.log
```

Behaviour:

- extract top errors
- send to LLM endpoint
- endpoint configured via environment variable

Example:

```bash
LOGSCOPE_LLM_ENDPOINT=https://...
```

Output:

- probable root cause summary
- contributing factors
- recommended next steps

Unit tests should mock API calls.

Commit separately:

```text
feat(explain): add LLM error explanation
```

---

# 8. Coding Standards

Requirements:

- type hints/types where supported
- modular design
- small focused functions
- docstrings/comments for non-obvious logic
- meaningful error messages
- deterministic tests
- no hidden global state

---

# 9. Acceptance Checklist

The project is complete only if all of the following pass:

- [ ] summary command works
- [ ] timeline command works
- [ ] grep command works
- [ ] json output works
- [ ] markdown output works
- [ ] malformed lines reported
- [ ] parser tests passing
- [ ] command tests passing
- [ ] 100 MB benchmark successful
- [ ] memory usage remains stable
- [ ] git history shows plan → incremental implementation

Before final submission, provide:

1. Test results
2. Coverage report
3. Benchmark results
4. Example command outputs
5. Remaining limitations