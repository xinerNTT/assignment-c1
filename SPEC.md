•	logscope summary app.log – counts by level (INFO / WARN / ERROR), top 5 error messages, first and last timestamp
•	logscope timeline app.log --bucket 15m – error count per time bucket as a text bar chart
•	logscope grep app.log --level ERROR --since "2026-10-01 09:00" – filtered lines
•	--format json|md on every command; md writes a report file
•	Handles a 100 MB log without loading it fully into memory
•	Malformed lines are counted and skipped; they never crash the tool
