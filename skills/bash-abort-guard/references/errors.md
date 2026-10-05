# Error lines the pairs replay (all thrown live by scripts/run_abort.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the bounded report instead.

- `Tool execution aborted`: sleep poll 240s foreground wait. Pair `bb-timeout`
- `Tool execution aborted`: node metrics full output foreground wait. Pair `bb-background`
- `Tool execution aborted`: foreground receipt wait with no bound. Pair `bb-receipt`
- `Tool execution aborted`: heavy cargo build in foreground. Pair `bb-build`
- `Tool execution aborted`: full test suite in one call. Pair `bb-slice`
- `Tool execution aborted`: two chained long checks in one call. Pair `bb-chain`
- `Tool execution aborted`: whole suite with no filter in one run. Pair `bb-chunk`
- `Tool execution aborted`: chained checks with no sequence. Pair `bb-single`
- `Tool execution aborted`: long inline script in one call. Pair `bb-file`
- `Tool execution aborted`: unbounded listing scan with no limit. Pair `bb-limit`
- `Tool execution aborted`: unbounded output flood with no cap. Pair `bb-output`
- `Tool execution aborted`: long run with no result reported. Pair `bb-report`
