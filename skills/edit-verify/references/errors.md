# Error lines the pairs replay (all thrown live by scripts/run_verify.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the verify-then-lint report instead.

- `Could not find oldString`: second edit without a fresh Read. Pair `ev-reread`
- `Could not find oldString`: follow-up edit typed from memory. Pair `ev-quote`
- `Could not find oldString`: LF oldString on CRLF lines. Pair `ev-endings`
- `no diff shown`: close with no hunks read. Pair `ev-diff`
- `Could not find oldString`: identical oldString retried as a fresh change. Pair `ev-noop`
- `multiple matches`: one short line in three places. Pair `ev-single`
- `no lint ran`: edit closed with pytest never executed. Pair `ev-lint`
- `never re-ran`: fix closed with the check never re-run. Pair `ev-rerun`
- `no error line`: paraphrased failure with no error line. Pair `ev-error`
- `no changed paths`: report with no paths and no results. Pair `ev-report`
- `scaffold text remains`: unverified rules with no source. Pair `ev-noscaffold`
- `pairs never ran`: class claimed fixed with run_verify never executed. Pair `ev-proof`
- `Could not find oldString`: tab-indented line matched with spaces. Pair `ev-tabs`
- `Could not find oldString`: trailing spaces trimmed from oldString. Pair `ev-trail`
- `Could not find oldString`: file changed after the read, stale oldString retried. Pair `ev-stale`
- `multiple matches`: short line in two places, widened with six surrounding lines. Pair `ev-widen`
- `Could not find oldString`: wrong-case oldString typed from memory. Pair `ev-case`
