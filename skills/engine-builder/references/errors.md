# Error lines the pairs replay (all thrown live by scripts/run_pairs.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the landed report instead.

- `Changed: none`: the empty report with no diff and no check lines. Pair `eb-lane-missing`
- `no edits`: the session did nothing it can name. Pair `eb-present-work`
- `Changed: none`: audit still failing, file untouched. Pair `eb-audit-file`
- `nothing to do`: smallest slice never attempted. Pair `eb-small-slice`
- `no edits`: shared cache lock stopped the run. Pair `eb-cache-lock`
- `no changes`: capability too big, nothing landed. Pair `eb-sub-slice`
- `no edits`: new crate added without searching first. Pair `eb-reuse-first`
- `nothing to do`: unwrap left on user input. Pair `eb-typed-errors`
- `Changed: none`: checks never ran. Pair `eb-check-trio`
- `no changes`: hot path still allocates per tick. Pair `eb-hot-path`
- `Changed: none`: dependency added without a feature gate. Pair `eb-dep-flag`
- `no edits`: report lists no paths and no results. Pair `eb-report`
