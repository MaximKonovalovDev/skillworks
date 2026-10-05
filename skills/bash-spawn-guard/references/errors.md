# Error lines the pairs replay (all thrown live by scripts/run_spawn.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the bounded report instead.

- `ChildProcess.kill`: detached check with no receipt to poll. Pair `bs-receipt`
- `ChildProcess.kill`: verbose foreground package install. Pair `bs-install`
- `ChildProcess.kill`: sleep poll foreground wait with no bound. Pair `bs-sleep`
- `ChildProcess.kill`: foreground wait with no receipt file. Pair `bs-background`
- `ChildProcess.kill`: full suite in one shell call. Pair `bs-suite`
- `ChildProcess.kill`: chained long checks in one call. Pair `bs-chain`
- `ChildProcess.kill`: full suite with no slice. Pair `bs-chunk`
- `ChildProcess.kill`: chained listing with no limit. Pair `bs-list`
- `ChildProcess.kill`: long inline probe script. Pair `bs-inline`
- `ChildProcess.kill`: inline probe with no file. Pair `bs-file`
- `ChildProcess.kill`: unbounded status check. Pair `bs-short`
- `ChildProcess.kill`: long run with no result reported. Pair `bs-report`
