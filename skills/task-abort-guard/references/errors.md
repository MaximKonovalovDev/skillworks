# Error lines the pairs replay (all thrown live by scripts/run_task.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the bounded report instead.

- `Tool execution aborted`: task fan-out parallel dispatch. Pair `ta-dispatch`
- `Tool execution aborted`: task parallel fan-out with no sequence. Pair `ta-sequence`
- `Tool execution aborted`: task foreground wait with no timeout. Pair `ta-background`
- `Tool execution aborted`: task receipt wait with no bound. Pair `ta-receipt`
- `Tool execution aborted`: large write in one call. Pair `ta-write`
- `Tool execution aborted`: large read in one call. Pair `ta-read`
- `Tool execution aborted`: large edit hunk in one call. Pair `ta-edit`
- `Tool execution aborted`: wide grep search with no scope. Pair `ta-narrow`
- `Tool execution aborted`: large write chunk with no slice. Pair `ta-slice`
- `Tool execution aborted`: full read with no limit. Pair `ta-limit`
- `Tool execution aborted`: whole-file edit with no chunk. Pair `ta-chunk`
- `Tool execution aborted`: long run with no result reported. Pair `ta-report`
- `Tool execution aborted`: task parallel build with no timeout. Pair `ta-task-timeout`
- `Tool execution aborted`: write unbounded chunk with no receipt. Pair `ta-write-receipt`
- `Tool execution aborted`: read unbounded offset with no window. Pair `ta-read-window`
- `Tool execution aborted`: edit stale text with no reread. Pair `ta-edit-reread`
- `Tool execution aborted`: grep unbounded repo search with no folder. Pair `ta-grep-scope`
