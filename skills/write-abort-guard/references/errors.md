# Error lines the pairs replay (all thrown live by scripts/run_write.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair writes one small chunk and prints the receipt instead.

- `Tool execution aborted: whole write in one call`: whole file sent in one call. Pair `wa-slice`
- `Tool execution aborted: whole write of one section`: section write with no slice. Pair `wa-chunk`
- `Tool execution aborted: reran the whole write`: whole write rerun after the abort. Pair `wa-halve`
- `Tool execution aborted: whole write retried`: retry at full width. Pair `wa-half`
- `Tool execution aborted: chained large writes`: chained writes in one session. Pair `wa-single`
- `Tool execution aborted: hammered write retries`: hammered retries after the abort. Pair `wa-once`
- `Tool execution aborted: write with no staging`: write with no staging and no limit. Pair `wa-stage`
- `Tool execution aborted: whole write of a large file`: large file with no staging. Pair `wa-first`
- `Tool execution aborted: foreground wait`: foreground wait on a long write. Pair `wa-back`
- `Tool execution aborted: long foreground write`: long write with no receipt. Pair `wa-poll`
- `Tool execution aborted: silent close`: silent close with no report. Pair `wa-report`
- `Tool execution aborted: repeat abort`: repeat abort with no record. Pair `wa-record`
