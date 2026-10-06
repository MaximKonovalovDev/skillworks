# Sources and licences (verified 2026-10-06)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/edit-identical/`).
- Licence: MIT. Verified 2026-10-06: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `edit-identical-noop` in `skills/edit-identical/references/target-class.json` (20 identical no-change misses in 48 h across 9 dirs, row DR-1006-10, scanned 2026-10-06; replayed live 2026-10-06: `No changes to apply: oldString and newString are identical.` in scratch under TEMP). Own MIT corpus, read live 2026-10-06.
- Licensed manual for the receipts: the two own MIT notes passed to `python -m book2skill make --in work/edit-identical-manual --name edit-identical` (refuse-the-no-op plus verify-then-report, own words, read live 2026-10-06; receipt `work/edit-identical/make.json`). No donor code or text copied.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real identical line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_edit_identical.py`.

Credit line for THIRD_PARTY_NOTICES.md: edit-identical (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-06; no outside text copied).
