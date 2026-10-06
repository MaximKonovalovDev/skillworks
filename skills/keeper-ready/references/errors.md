# Error lines the pairs replay (all thrown live by scripts/run_keeper.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the queue report instead.

- `Keeper readiness hold: no unclaimed ready work or changed evidence blind dispatch`: blind dispatch with no queue check first. Pair `kr-queue`
- `Keeper readiness hold: no unclaimed ready work or changed evidence empty batch`: empty batch with no changed evidence. Pair `kr-evidence`
- `Keeper readiness hold: no unclaimed ready work or changed evidence chained dispatch`: chained dispatches in a row. Pair `kr-single`
- `Keeper readiness hold: no unclaimed ready work or changed evidence seat no eligible work`: standing seat with no eligible work. Pair `kr-eligible`
- `Keeper readiness hold: no unclaimed ready work or changed evidence retried empty dispatch`: retried empty dispatch after the hold. Pair `kr-once`
- `Keeper readiness hold: no unclaimed ready work or changed evidence silent no report`: hold closed silent with no report. Pair `kr-report`
- `Keeper readiness hold: no unclaimed ready work or changed evidence blind no queue check`: blind dispatch with no queue check. Pair `kr-check`
- `Keeper readiness hold: no unclaimed ready work or changed evidence stale batch no verify`: stale batch with no evidence verify. Pair `kr-verify`
- `Keeper readiness hold: no unclaimed ready work or changed evidence chained silent seat`: chained seat reads closed silent. Pair `kr-list`
- `Keeper readiness hold: no unclaimed ready work or changed evidence repeated seat hammer`: repeated seat dispatch hammer. Pair `kr-seat`
- `Keeper readiness hold: no unclaimed ready work or changed evidence empty hammer no fallback`: empty dispatch hammered with no fallback. Pair `kr-fallback`
- `Keeper readiness hold: no unclaimed ready work or changed evidence silent repeat no record`: silent repeat with no dispatch record. Pair `kr-record`
