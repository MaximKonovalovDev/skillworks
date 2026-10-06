# Error lines the pairs replay (all thrown live by scripts/run_allow.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the single-call report instead.

- `prevents you from using this specific tool call`: git log piped to formatting. Pair `ba-single`
- `prevents you from using this specific tool call`: patch stat piped to formatting. Pair `ba-status`
- `prevents you from using this specific tool call`: lane helper piped to formatting. Pair `ba-nopipe`
- `prevents you from using this specific tool call`: health probe piped to convert. Pair `ba-direct`
- `prevents you from using this specific tool call`: checkout revert from the shell. Pair `ba-read`
- `prevents you from using this specific tool call`: restore edit from the shell. Pair `ba-edit`
- `prevents you from using this specific tool call`: wide grep chained to formatting. Pair `ba-grep`
- `prevents you from using this specific tool call`: file list piped to formatting. Pair `ba-glob`
- `prevents you from using this specific tool call`: two chained checks in one call. Pair `ba-seq`
- `prevents you from using this specific tool call`: guessed repo read from the shell. Pair `ba-sha`
- `prevents you from using this specific tool call`: test run chained to formatting. Pair `ba-log`
- `prevents you from using this specific tool call`: long run with no result reported. Pair `ba-report`
- `powershell -NoProfile`: nested shell chained to listing and formatting. Pair `ba-nested`
- `blocked path`: edit itself denied, stop and paste the patch. Pair `ba-blocked`
- `Start-Sleep`: sleep-prefixed health poll piped to convert. Pair `ba-sleep`
- `node -e`: inline code chained to echo and formatting. Pair `ba-inline`
- `tools/lanes.mjs`: helper piped to formatting. Pair `ba-lanes`
