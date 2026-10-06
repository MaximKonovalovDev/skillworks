# Error lines the pairs replay (all thrown live by scripts/run_read.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the sliced lines or the receipt instead.

- `Tool execution aborted: unbounded full read`: whole file pulled in one call. Pair `ra-slice`
- `Tool execution aborted: full read of a section`: section read with no slice. Pair `ra-check`
- `Tool execution aborted: reran the whole read`: whole read rerun after the abort. Pair `ra-halve`
- `Tool execution aborted: whole read retried`: retry at full width. Pair `ra-half`
- `Tool execution aborted: chained large reads`: chained reads in one session. Pair `ra-single`
- `Tool execution aborted: hammered slice retries`: hammered retries after the abort. Pair `ra-once`
- `Tool execution aborted: read with no offset`: read with no offset and no limit. Pair `ra-size`
- `Tool execution aborted: unbounded section read`: section read with no size check. Pair `ra-first`
- `Tool execution aborted: foreground wait`: foreground wait on a long read. Pair `ra-back`
- `Tool execution aborted: long foreground read`: long read with no receipt. Pair `ra-poll`
- `Tool execution aborted: silent close`: silent close with no report. Pair `ra-report`
- `Tool execution aborted: repeat abort`: repeat abort with no record. Pair `ra-record`
