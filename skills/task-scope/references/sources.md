# Sources and licences (verified 2026-10-06)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/task-scope/`).
- Licence: MIT. Verified 2026-10-06: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `task-scope-lead-orchestrator` in `skills/task-scope/references/target-class.json` (85 Task cancelled errors in 48 h across 5 repos, row DR-1006-2; `python tools/fleet_failures.py compare task-scope` prints `task-scope: before 0 now 133 UP` on 2026-10-06, 0 loads). Own MIT corpus, read live 2026-10-06.
- Licensed manual for the receipts: the two own MIT notes passed to `python -m book2skill make --in <folder> --name task-scope` (claim-before-dispatch plus bounded fan-out plus slice-with-receipt, own words, read live 2026-10-06).
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real Task cancelled line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_task_scope.py`.

Credit line for THIRD_PARTY_NOTICES.md: task-scope (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-06; no outside text copied).
