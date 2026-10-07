# Error lines the pairs replay (all thrown live by scripts/run_repro.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the repro report instead.

- `aborted after long foreground task call with no repro`: abort with no repro on record. Pair `rp-repro`
- `aborted dispatching the whole task with nothing learned`: abort on the whole call. Pair `rp-slice`
- `aborted after assumed-cause fix dispatch`: abort on an assumed cause. Pair `rp-before`
- `aborted on fix claimed done with no failing-before proof`: abort with no before proof. Pair `rp-verify`
- `aborted twice on the same unreproduced step`: abort on the second redispatch. Pair `rp-stop`
- `aborted on kitchen-sink dispatch with five goals`: abort on the kitchen-sink call. Pair `rp-minimal`
- `aborted on builder report with no bounded run`: abort with no bounded run. Pair `rp-timeout`
- `aborted on suspected regression with no failing run`: abort with no failing run. Pair `rp-quote`
- `aborted on proposed fix with no after proof`: abort with no after proof. Pair `rp-after`
- `aborted on long task with no riskiest-step repro`: abort with no riskiest-step run. Pair `rp-risk`
- `aborted on multi-symptom report with no isolated repro`: abort with no isolated repro. Pair `rp-first`
- `aborted on flaky step with no recorded outcomes`: abort with no recorded outcomes. Pair `rp-result`
