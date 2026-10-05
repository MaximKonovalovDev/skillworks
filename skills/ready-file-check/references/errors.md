# Error lines the pairs replay (all thrown live by scripts/run_ready.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the list-first report instead.

- `File not found`: hardcoded direct read of a ready file. Pair `rf-list`
- `File not found`: stale ready path read from memory. Pair `rf-batch`
- `File not found`: hardcoded name after the keeper moved it. Pair `rf-exists`
- `File not found`: already consumed file re-read. Pair `rf-done`
- `File not found`: numbered ready file with offset, file gone. Pair `rf-offset`
- `File not found`: loop crashed on the first miss. Pair `rf-loop`
- `File not found`: standing run guessed a ready path. Pair `rf-start`
- `File not found`: duplicate packet take. Pair `rf-pick`
- `File not found`: queue state guessed from memory. Pair `rf-state`
- `File not found`: resume re-ran a done item. Pair `rf-resume`
- `File not found`: sweep stopped on a miss. Pair `rf-sweep`
- `File not found`: empty run reported nothing. Pair `rf-report`
