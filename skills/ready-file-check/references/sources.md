# Sources and licences (verified 2026-10-05)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/ready-file-check/`).
- Licence: MIT. Verified 2026-10-05: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `ready-file-check-missing` in `skills/ready-file-check/references/target-class.json` (22 File not found read misses in 48 h across 5 repos, row DR-1005-3, re-scanned live 2026-10-05; brief cites 22 at 2026-10-05T09:32Z). Own MIT corpus, read live 2026-10-05.
- Licensed manual for the receipts: the two own MIT notes passed to `python -m book2skill make --in <folder> --name ready-file-check` (list-first plus batch-doc plus existence-check, own words, read live 2026-10-05; receipt `work/ready-file-check/make.json`).
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real File not found line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_ready_file_check.py`.

Credit line for THIRD_PARTY_NOTICES.md: ready-file-check (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-05; no outside text copied).
