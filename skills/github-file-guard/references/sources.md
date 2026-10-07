# Sources and licences (verified 2026-10-07)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/github-file-guard/`).
- Licence: MIT. Verified 2026-10-07: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan, class `github-file-guard` in `skills/github-file-guard/references/target-class.json` (40 github_get_file_contents path misses in 48 h in 8 repos, row DR-1007-14, scanned 2026-10-07; replayed live 2026-10-07: `Failed to get file contents` for a guessed path in scratch under TEMP). Own MIT corpus, read live 2026-10-07.
- Distinct from DR-1006-1 DONE (skill `webfetch-retry`, webfetch 403 plus 404 misses) plus BK-1006-3 DONE (skill `gh-cli-manual`, gh CLI surface as book knowledge) plus DR-1007-8 READY (fetch-content tool status fallback) plus DR-1007-6 DONE (skill `batch-first`, GitHub MCP timeout batching): this skill owns the github MCP get_file_contents guessed-path miss with a list-first verify gate only.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real path-miss line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_github_file_guard.py`.

Credit line for THIRD_PARTY_NOTICES.md: github-file-guard (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-07; no outside text copied).
