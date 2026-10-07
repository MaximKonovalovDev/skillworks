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
- `ChildProcess.kill`: chained 4 listings plus git plus node in one call. Pair `bs-chain4`
- `ChildProcess.kill`: Start-Process clone plus Start-Sleep 20 with no receipt. Pair `bs-clone`
- `ChildProcess.kill`: Start-Process shim plus Start-Sleep 3 plus double poll. Pair `bs-shim`
- `ChildProcess.kill`: chained detect checks with redirects piped tail. Pair `bs-detect`
- `ChildProcess.kill`: npm run suites bare with no slice. Pair `bs-suites`
- `ChildProcess.kill`: Start-Sleep 45 plus redeploy lane poll with no receipt. Pair `bs-redeploy`
- `ChildProcess.kill`: full cargo test heavy build in one shell call. Pair `bs-cargo`
- `ChildProcess.kill`: double node test full run piped with no slice. Pair `bs-nodetest`
- `ChildProcess.kill`: triple detect checks plus board grep chained in one call. Pair `bs-detect3`
- `ChildProcess.kill`: chained proof plus check scans in one call. Pair `bs-proofchain`
- `ChildProcess.kill`: chained git status plus git log plus node score in one call. Pair `bs-gitstat`
- `ChildProcess.kill`: full python pytest run in one shell call. Pair `bs-pytest`
- `ChildProcess.kill`: verbose npm install foreground with no receipt. Pair `bs-npminstall`
- `ChildProcess.kill`: Start-Sleep poll of log file with no timeout. Pair `bs-logpoll`
- `ChildProcess.kill`: long Get-Content piped tail select in one call. Pair `bs-longpipe`
- `ChildProcess.kill`: piped cargo single test with Select-String tail in one call. Pair `bs-cargopipe`
- `ChildProcess.kill`: chained git status plus batch read plus board grep in one call. Pair `bs-batchchain`
- `ChildProcess.kill`: chained lock show plus diff plus listing plus trials read in one call. Pair `bs-lockchain`
- `ChildProcess.kill`: bare node rome-score with exit check in one call. Pair `bs-romescore`
- `ChildProcess.kill`: chained fleet scan plus loads in one call. Pair `bs-scanchain`
