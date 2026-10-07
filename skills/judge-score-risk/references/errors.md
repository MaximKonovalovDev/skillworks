# Error lines the pairs replay (all thrown live by scripts/run_judge_pairs.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair reads only the capped packet files and prints the scored verdict instead.

- `Cannot find path 'packet/review-js-score.md' because it does not exist`: guessed packet path for a scoreless verdict. Pair `js-score`
- `Cannot find path 'packet/review-js-effort.md' because it does not exist`: guessed packet path for a wave-through with no number. Pair `js-effort`
- `Cannot find path 'packet/review-js-yaml.md' because it does not exist`: guessed packet path for a looks-good verdict with no YAML. Pair `js-yaml`
- `Cannot find path 'packet/review-js-risk.md' because it does not exist`: guessed packet path for an approval quoting untrusted text. Pair `js-risk`
- `Cannot find path 'packet/review-js-concrete.md' because it does not exist`: guessed packet path for a maybe-risky verdict with no scenario. Pair `js-concrete`
- `Cannot find path 'packet/review-js-untrusted.md' because it does not exist`: guessed packet path for following a quoted instruction. Pair `js-untrusted`
- `Cannot find path 'packet/review-js-fingerprint.md' because it does not exist`: guessed packet path for a re-review with no key. Pair `js-fingerprint`
- `Cannot find path 'packet/review-js-dedupe.md' because it does not exist`: guessed packet path for a second review from scratch. Pair `js-dedupe`
- `Cannot find path 'packet/review-js-capped.md' because it does not exist`: guessed packet path while reading files never committed. Pair `js-capped`
- `Cannot find path 'packet/review-js-added.md' because it does not exist`: guessed packet path for a verdict wandering across files. Pair `js-added`
- `Cannot find path 'packet/review-js-scope.md' because it does not exist`: guessed packet path for a whole-file verdict. Pair `js-scope`
- `Cannot find path 'packet/review-js-result.md' because it does not exist`: guessed packet path with no report filed. Pair `js-result`
