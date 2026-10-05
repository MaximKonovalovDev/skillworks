# Sources and licences (verified 2026-10-05)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/read-offset-guard/`).
- Licence: MIT. Verified 2026-10-05: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `read-offset` in `skills/read-offset-guard/references/target-class.json` (18 Offset out of range read errors in 48 h across 5 repos, row DR-1005-8, scanned 2026-10-05T14:35Z; replayed live 2026-10-05: `Offset 100 is out of range for this file (1 lines)` on a 1-line file at offset 100). Own MIT corpus, read live 2026-10-05.
- Licensed manual for the receipts: the two own MIT notes passed to `python -m book2skill make --in <folder> --name read-offset-guard` (count-first-clamp plus tail-and-recount, own words, read live 2026-10-05; receipt `work/read-offset-guard/make.json`). The ranger pager (ranger/ranger, GPL-3.0) informed the clamp idea only; no donor code or text copied.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real Offset out of range line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_read_offset_guard.py`.

Credit line for THIRD_PARTY_NOTICES.md: read-offset-guard (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-05; no outside text copied).
