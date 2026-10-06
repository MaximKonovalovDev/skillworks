# Error lines the pairs replay (all thrown live by scripts/run_pairs.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the check-first report instead.

- `Repository not found`: the wiki question guessed an unindexed repo. Pair `rr-b01`
- `does not point to a file`: the file read guessed a path never listed. Pair `rr-b02`
- `404`: a guessed raw host URL that does not exist. Pair `rr-b03`
- `could not resolve ref`: the read assumed a branch ref that does not resolve. Pair `rr-b04`
- `Repository not found`: a second repo asked without calling the repos record. Pair `rr-b05`
- `does not point to a file`: a directory path asked with the file-contents call. Pair `rr-b06`
- `guessed`: the full read guessed instead of calling the repos record first. Pair `rr-g01`
- `Repository not found`: the docs summary never checked the indexed state. Pair `rr-g02`
- `could not resolve ref`: the pinned release ref never resolved from the record. Pair `rr-g03`
- `does not point to a file`: a helper reused with no licence note and no confirmed path. Pair `rr-g04`
- `does not point to a file`: the retry helper location guessed, never confirmed. Pair `rr-g05`
- `Repository not found`: the report lists no record, no ref, and no results. Pair `rr-g06`
- `Request timed out`: the contents call guessed without a repos record and timed out. Pair `rr-b07`
- `failed to get reference for branch`: the read assumed a default branch without the repos record. Pair `rr-b08`
- `does not point to a file`: a nested path guessed without a directory listing. Pair `rr-b09`
- `Repository not found`: a third repo asked without calling the repos record. Pair `rr-b10`
- `404`: a guessed raw host URL on the main branch that does not exist. Pair `rr-b11`
