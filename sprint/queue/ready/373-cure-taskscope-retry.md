---
role: builder
title: cure task-scope retry after crash (pinned, light)
---
Goal: finish DR-1006-2 (task Task cancelled after dispatch, 42 a day; engine2040 43 plus forge 28, 0 loads) without repeating the crash: pinned row, light test load, resume-safe. The crashed run claimed `DR-1006-2 | builder-cure | 2026-10-09T10:16Z | skills/task-scope/` and touched no skill file (tree shows no skills/task-scope/ diff); reuse that claim, do not double-claim.

Scope: `skills/task-scope/`, `evals/task-scope_trials.jsonl`, `tests/test_task_scope.py` (name may differ; find it), `team/p3.md` line. Read-only everywhere else. Never commit or push. Version bump only if the newest failures show shapes the skill lacks (add 5 pairs, bump version, never delete a passing pair); else re-proof with resealed proofs and say so.

Proof:
- Red replay: one bad Task-cancelled case fails bare and passes with the skill; paste both lines.
- `python tests/live_proof.py task-scope` ends proven; `python tools/skill_lint.py check --skill skills/task-scope` exit 0.
- `python tools/skill_trial.py grade --skill task-scope` runs with/without plus lift (needs 0.3).
- Focused test file only (`-q`), plus `node sprint/check.mjs` PASS. NO full suite (that stays the judge's job; long runs keep crashing).
- `python tools/fleet_failures.py lanes` refresh; append ONE line to `team/p3.md`.

Stop: M 25 min hard box; at 20 min stop building and report what is proven. The second identical failure ends the step. End with `RESULT: DONE - <skill change plus numbers> | proof: <live plus grade one-liners>` or `RESULT: PARTIAL - <what is proven, what is missing> | proof: <lines you have>`.
