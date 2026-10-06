# Sources and licences (verified 2026-10-05)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/task-abort-guard/`).
- Licence: MIT. Verified 2026-10-05: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `task-abort-othertools` in `skills/task-abort-guard/references/target-class.json` (36 non-bash Tool execution aborted errors in 48 h across 7 repos, row DR-1005-5, scanned 2026-10-05T10:29Z). Own MIT corpus, read live 2026-10-05. Bump v1.1.0 adds 5 pairs from the 2026-10-06T23:36Z scan (task 33 plus write 19 plus read 58 plus edit 25 plus grep 6 Tool execution aborted in 48 h): ta-task-timeout, ta-write-receipt, ta-read-window, ta-edit-reread, ta-grep-scope. Own MIT corpus, read live 2026-10-06.
- Licensed manual for the receipts: the two own MIT notes passed to `python -m book2skill make --in <folder> --name task-abort-guard` (bound-calls plus slice-report, own words, read live 2026-10-05; receipt `work/task-abort-guard/make.json`).
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real Tool execution aborted line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_task_abort_guard.py`.

Credit line for THIRD_PARTY_NOTICES.md: task-abort-guard (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-05; no outside text copied).
