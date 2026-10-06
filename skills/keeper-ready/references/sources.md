# Sources and licences (verified 2026-10-06)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/keeper-ready/`).
- Licence: MIT. Verified 2026-10-06: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `keeper-ready-hold` in `skills/keeper-ready/references/target-class.json` (20 Keeper holds in 48 h, row DR-1006-11, scanned 2026-10-06; replayed live 2026-10-06: `Keeper readiness hold: no unclaimed ready work or changed evidence` in scratch under TEMP). Own MIT corpus, read live 2026-10-06.
- Licensed manual for the receipts: the two own MIT notes passed to `python -m book2skill make --in <folder> --name keeper-ready` (queue-first plus evidence-verify, own words, read live 2026-10-06; receipt `work/keeper-ready/make.json`). No donor code or text copied.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real Keeper hold line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_keeper_ready.py`.

Credit line for THIRD_PARTY_NOTICES.md: keeper-ready (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-06; no outside text copied).
