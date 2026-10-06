# Error lines the pairs replay (all thrown live by scripts/run_identical.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the verify report instead.

- `already satisfied`: identical no-op on an already-satisfied request. Pair `ei-refuse`
- `applied twice`: identical no-op after the same text was applied twice. Pair `ei-diff`
- `typed from memory`: identical no-op typed from memory. Pair `ei-quote`
- `stale reread`: identical no-op on a stale reread. Pair `ei-fresh`
- `whole block copied`: identical no-op with a whole block copied as both sides. Pair `ei-narrow`
- `retried three times`: identical no-op retried three times. Pair `ei-single`
- `broad block sent`: identical no-op with a broad block sent. Pair `ei-hunk`
- `closed unverified`: identical no-op closed with no check. Pair `ei-check`
- `no diff read`: identical no-op with no diff read. Pair `ei-verify`
- `request satisfied`: identical no-op on a satisfied request. Pair `ei-already`
- `broad old kept`: identical no-op with a broad old kept. Pair `ei-small`
- `closed silent`: identical no-op closed with no report. Pair `ei-result`
