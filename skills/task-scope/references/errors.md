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
