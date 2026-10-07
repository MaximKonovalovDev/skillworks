# Sources and licences (verified 2026-10-07)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/write-abort-guard/`).
- Licence: MIT. Verified 2026-10-07: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `write-abort-longwrite` in `skills/write-abort-guard/references/target-class.json` (10 write aborts in 48 h, row DR-1007-12, scanned 2026-10-07; replayed live 2026-10-07: `Tool execution aborted` in scratch under TEMP). Own MIT corpus, read live 2026-10-07.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real abort line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_write_abort_guard.py`.

Credit line for THIRD_PARTY_NOTICES.md: write-abort-guard (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-07; no outside text copied).
