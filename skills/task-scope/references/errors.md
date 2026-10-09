# Error lines the pairs replay (all thrown live by scripts/run_scope.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the scoped report instead.

- `Task cancelled`: parallel dispatch of two queue items. Pair `ts-claim`
- `Task cancelled`: duplicate dispatch of a claimed item. Pair `ts-duplicate`
- `Task cancelled`: re-dispatch of live running work. Pair `ts-running`
- `Task cancelled`: wide fan-out with stragglers. Pair `ts-fanout`
- `Task cancelled`: long run with no checkpoint. Pair `ts-slice`
- `Task cancelled`: dispatch after the stop line. Pair `ts-eligible`
- `Task cancelled`: parallel two items, second cancelled. Pair `ts-single`
- `Task cancelled`: picked item already claimed. Pair `ts-pick`
- `Task cancelled`: scout batch stragglers. Pair `ts-batch`
- `Task cancelled`: long repair with no receipt. Pair `ts-resume`
- `Task cancelled`: rerun duplicates work. Pair `ts-idempotent`
- `Task cancelled`: run with no result reported. Pair `ts-report`
- `Task cancelled`: same description dispatched twice in one session. Pair `ts-dupdesc`
- `Task cancelled`: six parallel runs at once with stragglers. Pair `ts-onefan`
- `Task cancelled`: land batch fired at once with stragglers. Pair `ts-landbatch`
- `Task cancelled`: orchestrator wide fan-out with stragglers. Pair `ts-orchseq`
- `Task cancelled`: same description dispatched twice, second cancelled as duplicate. Pair `ts-descclaim`
- `Task cancelled`: retry in a fresh lane without a claim. Pair `ts-retryseq`
- `Task cancelled`: four parallel captures at once with stragglers. Pair `ts-capbound`
- `Task cancelled`: two research topics at once as duplicates. Pair `ts-topicdedupe`
- `Task cancelled`: vague single token with no claim. Pair `ts-vagueclaim`
- `Task cancelled`: repair chain of three fixes with no receipt. Pair `ts-repairchain`
