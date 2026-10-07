# Sources and licences (verified 2026-10-07)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/webfetch-retry/`).
- Licence: MIT. Verified 2026-10-07: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan, class `webfetch-retry` in `skills/webfetch-retry/references/target-class.json` (12 Request timed out misses in 48 h in 2 repos, row DR-1007-3, scanned 2026-10-07; replayed live 2026-10-07: `Request timed out after 30000ms` in scratch under TEMP). Own MIT corpus, read live 2026-10-07.
- Distinct from DR-1006-7 DONE (skill `websearch-retry`, websearch backend-busy plus missing-key shapes) and DR-1006-1 DONE (skill `fetch-github-first`, webfetch 403 plus 404 shapes): this skill owns the webfetch timeout shape only.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real timeout line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_webfetch_retry.py`.

Credit line for THIRD_PARTY_NOTICES.md: webfetch-retry (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-07; no outside text copied).
