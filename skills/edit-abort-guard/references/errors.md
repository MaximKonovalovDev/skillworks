# Error lines the pairs replay (all thrown live by scripts/run_edit.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair lands its hunk and prints the diff or the receipt report instead.

- `Tool execution aborted: unbounded whole-file edit`: whole file edited in one call. Pair `ea-slice`
- `Tool execution aborted: section edit with no slice`: section edit with no slice. Pair `ea-check`
- `Tool execution aborted: reran the whole edit`: whole edit rerun after the abort. Pair `ea-halve`
- `Tool execution aborted: whole edit retried`: retry at full width. Pair `ea-half`
- `Tool execution aborted: chained large edits`: chained edits in one session. Pair `ea-single`
- `Tool execution aborted: hammered edit retries`: hammered retries after the abort. Pair `ea-once`
- `Tool execution aborted: edit with no scope`: edit with no scope and no limit. Pair `ea-size`
- `Tool execution aborted: unbounded section edit`: section edit with no size check. Pair `ea-first`
- `Tool execution aborted: foreground wait`: foreground wait on a long edit. Pair `ea-back`
- `Tool execution aborted: long foreground edit`: long edit with no receipt. Pair `ea-poll`
- `Tool execution aborted: silent close`: silent close with no report. Pair `ea-report`
- `Tool execution aborted: repeat abort`: repeat abort with no record. Pair `ea-record`
