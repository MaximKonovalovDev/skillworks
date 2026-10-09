# Sources and licences (verified 2026-10-06)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/read-offset-guard/`).
- Licence: MIT. Verified 2026-10-06: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `read-offset` in `skills/read-offset-guard/references/target-class.json` (33 Offset out of range read errors in 48 h, row DR-1006-5, scanned 2026-10-06T17:17Z; replayed live 2026-10-06: `Offset 60 is out of range for this file (3 lines)` on a 3-line scratch file at offset 60). Own MIT corpus, read live 2026-10-06. Version bump 1.1.0 adds 5 pairs from the newest failures (315/44, 90/32, 600/542, 620/541, 30/28); version bump 1.2.0 adds 5 pairs from the newest failures (180/133, 600/544, 1997/0 empty, 135/133, 600/534); version bump 1.3.0 adds 5 pairs from the newest failures (620/588, 615/557, 620/555, 560/554, 100000/32); version 1.3.1 re-lands that 1.3.0 coverage (lost in a later tree, SKILL rule plus errors index restored) alongside ro-index547 (620/547); version bump 1.4.0 adds 5 pairs from the newest failures (84/27, 1735/1734, 36/32, 14/13, 7593/106) plus the missing SKILL rule for ro-past27; no pair that passes was deleted.
- Licensed manual for the receipts: the two own MIT notes passed to `python -m book2skill make --in <folder> --name read-offset-guard` (count-first-clamp plus tail-and-recount, own words, read live 2026-10-05; receipt `work/read-offset-guard/make.json`). The ranger pager (ranger/ranger, GPL-3.0) informed the clamp idea only; no donor code or text copied.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real Offset out of range line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_read_offset_guard.py`.

Credit line for THIRD_PARTY_NOTICES.md: read-offset-guard (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-05; no outside text copied).
