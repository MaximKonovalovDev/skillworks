# Error lines the pairs replay (all thrown live by scripts/run_grep.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the chunked report instead.

- `whole tree`: miss grepping the whole tree with no scope. Pair `gl8-b01`
- `unfiltered grep`: miss on an unfiltered grep in center. Pair `gl8-b02`
- `whole repo`: miss grepping the whole repo with no glob. Pair `gl8-b03`
- `single grep`: miss on a single grep over 8 repos. Pair `gl8-b04`
- `unbounded grep`: miss on an unbounded grep with no hit limit. Pair `gl8-b05`
- `broad regex`: miss on a broad regex grep with no literal. Pair `gl8-b06`
- `no scope`: miss searching docs in works with no scope. Pair `gl8-g01`
- `spawn guard`: miss finding the spawn guard across the whole tree. Pair `gl8-g02`
- `keeper check`: miss locating the keeper check with an unfiltered sweep. Pair `gl8-g03`
- `single call`: miss counting callers with a single call in forge. Pair `gl8-g04`
- `lane writer`: miss finding the lane writer with a broad regex in asset-vault. Pair `gl8-g05`
- `no chunks`: miss reporting a sweep over center plus works with no chunks. Pair `gl8-g06`
