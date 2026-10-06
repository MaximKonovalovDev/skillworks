# Sources and licences (verified 2026-10-06)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/websearch-retry/`).
- Licence: MIT. Verified 2026-10-06: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `websearch-retry` in `skills/websearch-retry/references/target-class.json` (149 websearch misses in 48 h, 82 backend busy plus 66 missing key plus 1 timeout, row DR-1006-7, scanned 2026-10-06; replayed live 2026-10-06: `StatusCode: non 2xx status code (503 POST https://mcp.exa.ai/mcp)` in scratch under TEMP). Own MIT corpus, read live 2026-10-06.
- Licensed manual for the receipts: the two own MIT notes passed to `python -m book2skill make --in <folder> --name websearch-retry` (retry-once-with-backoff plus guard-the-shape, own words, read live 2026-10-06; receipt `work/websearch-retry/make.json`). No donor code or text copied.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real busy, shape, or timeout line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_websearch_retry.py`.

Credit line for THIRD_PARTY_NOTICES.md: websearch-retry (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-06; no outside text copied).
