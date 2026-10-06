# Sources and licences (verified 2026-10-07)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/edit-abort-guard/`).
- Licence: MIT. Verified 2026-10-07: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `edit-abort-longedit` in `skills/edit-abort-guard/references/target-class.json` (25 edit aborts in 48 h across 9 repos, row DR-1006-13, scanned 2026-10-06; replayed live 2026-10-07: `Tool execution aborted` on edit in the state failures.json). Own MIT corpus, read live 2026-10-07.
- Licensed manual for the receipts: the two own MIT notes passed to `python -m book2skill make --in work/edit-abort-guard-manual --name edit-abort-guard` (slice-to-one-hunk discipline, own words, read live 2026-10-07; receipt `work/edit-abort-guard/make.json`). No donor code or text copied.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real abort line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_edit_abort_guard.py`.

Credit line for THIRD_PARTY_NOTICES.md: edit-abort-guard (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-07; no outside text copied).
