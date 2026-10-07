---
role: builder
title: repair cure DR-1006-9 abort-guard version bump
chain: repair
of: builder-cure-abort
writer: builder
attempt: 2
origin_title: cure DR-1006-9 abort-guard version bump
---
The judge failed builder-cure-abort. Its verdict, cut:
<task id="ses_eec34ee65ffeJEbItQC6klEgkC" state="completed"> <task_result> VERDICT: FAIL Changed (e6579ba): bash-abort-guard v1.1.0, pairs 12→18 (+6 heavy-runner), SKILL.md+errors.md+trials; only 7 owned files (skills/bash-abort-guard/, evals/bash-abort-guard_trials.jsonl), no scope drift, names clean. Reran: `live_proof` → "proven. 6 passed in 22.85s" PASS (packet: 6/4.89s); lint → "rules 18, locators 36, pairs 36, body 742 tokens RESULT PASS" (matches packet 18/742); `test_bash_abort_guard.py` → 3 passed 3 skipped; `check.mjs` → 20/0/0 PASS. Not verified: trial grade 18×1.0/0.0 + 3 with/without cases (not rerun); full `pytest -q` green (heavy runs abort this shell); `fleet_failures round-line --check` → ChildProcess.kill abort twice; `Get-ChildItem -Recurse` aborts (Glob alt: no export dirs); record `done/builder-cure-abort.md` missing at cited path. One real thing: pairs.json now holds 18 (reran count=18) — coverage moved, not paperwork — but F2P class-halve needs 48h adoption per row, so done-when as written is partly met = FAIL. Revert: `git revert --no-commit e6579ba` (then re-land after grade + full-suite proof pasted). </task_result> </task>

Goal: fix exactly what the verdict names. Scope: the files of the original packet (C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-abort-review.md). Proof: the original proof plus the verdict's failing check. Stop: M 30 min; one repair only. End with the RESULT line.

Keeper facts: run builder-cure-abort-review (@judge), review abort-guard bump (a fleet failure to a proven skill).
VERDICT: FAIL
Changed (e6579ba): bash-abort-guard v1.1.0, pairs 12→18 (+6 heavy-runner), SKILL.md+errors.md+trials; only 7 owned files (skills/bash-abort-guard/, evals/bash-abort-guard_trials.jsonl), no scope drift, names clean.
