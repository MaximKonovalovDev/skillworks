# Sources and licences (verified 2026-10-06)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/read-abort-guard/`).
- Licence: MIT. Verified 2026-10-06: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `read-abort-longread` in `skills/read-abort-guard/references/target-class.json` (53 read aborts in 48 h, row DR-1006-12, scanned 2026-10-06; replayed live 2026-10-06: `Tool execution aborted` in scratch under TEMP). Own MIT corpus, read live 2026-10-06.
- Licensed manual for the receipts: the two own MIT notes passed to `python -m book2skill make --in work/read-abort-guard-manual --name read-abort-guard` (slice-plus-halve discipline, own words, read live 2026-10-06; receipt `work/read-abort-guard/make.json`). No donor code or text copied.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real abort line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_read_abort_guard.py`.

Credit line for THIRD_PARTY_NOTICES.md: read-abort-guard (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-06; no outside text copied).
