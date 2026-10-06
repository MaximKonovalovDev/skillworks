# Error lines the pairs replay (all thrown live by scripts/run_map.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the listing report instead.

- `File not found: owner/name/.opencode/repomap.md blind read`: blind map read with no listing first. Pair `rm-list`
- `File not found: owner/name/other/repomap.md guessed path`: guessed map path in another folder. Pair `rm-glob`
- `File not found: owner/name/repomap.md chained across folders`: chained missing reads across folders. Pair `rm-single`
- `File not found: owner/name/repomap.md blind read no listing`: map read with no folder listing first. Pair `rm-check`
- `File not found: owner/name/repomap.md identical retry hammer`: identical missing read retried in a row. Pair `rm-once`
- `File not found: owner/name/repomap.md no report silent`: missing map read closed with no report. Pair `rm-report`
- `File not found: owner/name/repomap.md blind guess`: blind guessed map read. Pair `rm-read`
- `File not found: owner/name/repomap.md guessed blind`: guessed blind map path. Pair `rm-find`
- `File not found: owner/name/repomap.md chained silent`: chained reads closed silent. Pair `rm-one`
- `File not found: owner/name/repomap.md repeated hammer`: identical map read repeated. Pair `rm-miss`
- `File not found: owner/name/repomap.md guessed hammer`: guessed map path hammered. Pair `rm-fallback`
- `File not found: owner/name/repomap.md silent repeat`: missing map read repeated silent. Pair `rm-record`
