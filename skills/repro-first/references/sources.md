# Sources and licences (verified 2026-10-07)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/repro-first/`).
- Licence: MIT. Verified 2026-10-07: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan, class `repro-first` in `skills/repro-first/references/target-class.json` (9 task Tool execution aborted misses in 48 h in 5 repos, row DR-1007-5, scanned 2026-10-07; replayed live 2026-10-07: `Tool execution aborted` in scratch under TEMP). Own MIT corpus, read live 2026-10-07.
- Distinct from DR-1006-9 READY (skill `bash-abort-guard`, bash foreground aborts) plus DR-1006-12 DONE (skill `read-abort-guard`, read aborts) plus DR-1006-13 DONE (skill `edit-abort-guard`, edit aborts): this skill owns the task-dispatch abort shape only.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real abort line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_repro_first.py`.

Credit line for THIRD_PARTY_NOTICES.md: repro-first (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-07; no outside text copied).
