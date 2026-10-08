# Sources and licences (verified 2026-10-08)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/grep-overflow-guard/`).
- Licence: MIT. Verified 2026-10-08: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan, class `grep-overflow-guard` in `skills/grep-overflow-guard/references/target-class.json` (29 Ripgrep JSON record exceeded misses in 48 h in 8 repos, row DR-1007-18, scanned 2026-10-08; replayed live 2026-10-08: `Ripgrep JSON record exceeded N bytes` for a whole-tree search in scratch under TEMP). Own MIT corpus, read live 2026-10-08.
- Distinct from BK-1007-1 DONE (skill `ripgrep-search`, ripgrep precision) plus BK-1007-4 DONE (skill `fd-find`, fd file-find scoping): this skill owns the grep tool JSON overflow fallback to a chunked narrow search only.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real overflow line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_grep_overflow_guard.py`.

Credit line for THIRD_PARTY_NOTICES.md: grep-overflow-guard (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-08; no outside text copied).
