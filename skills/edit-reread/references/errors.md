# Error lines the pairs replay (all thrown live by scripts/run_pairs.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the reread-first report instead.

- `Could not find oldString`: guessed oldString without a fresh Read. Pair `er-read-first`
- `Could not find oldString`: LF oldString on CRLF lines. Pair `er-crlf`
- `Could not find oldString`: spaces typed over tabs. Pair `er-tabs`
- `Could not find oldString`: trailing spaces dropped. Pair `er-trailing`
- `Could not find oldString`: file changed after the last Read. Pair `er-stale`
- `Could not find oldString`: oldString typed from memory. Pair `er-memory`
- `multiple matches`: one short line in five places. Pair `er-unique`
- `multiple matches`: ambiguous single edit refused by count. Pair `er-count`
- `multiple matches`: anchored on a unique neighbor. Pair `er-anchor`
- `multiple matches`: replaceAll needs a verified count. Pair `er-replace-all`
- `Could not find oldString`: identical oldString and newString is a no-op. Pair `er-noop`
- `Could not find oldString`: report with no paths and no results. Pair `er-report`
