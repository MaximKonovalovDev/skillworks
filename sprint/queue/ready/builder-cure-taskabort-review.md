---
role: judge
title: review task-abort-guard bump (weakest fallback)
chain: review
of: builder-cure-weakest13
writer: builder
attempt: 1
origin_title: cure weakest installed bump r13
---
Review builder-cure-weakest13, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-weakest13.md. Rerun its proof yourself, read its diff. There is no open row for this bump (dry fallback on the weakest FLEET skill); judge the work product itself: the bump must add 5 pairs from newest failures, delete none passing, and re-prove green with a red fails-before. You never edit.

Lead scoping (binding): no 48 h halving applies (no row); judge pair growth + proofs + red replay. Concurrent dirty files are out of scope — judge only skills/task-abort-guard/, evals/task-abort-guard_trials.jsonl, tests/test_task_abort_guard.py.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters; (c) privacy: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: the diff has a test that failed before and passes now or pairs moved 12->17 with run proof. Moved nothing is FAIL "paperwork".

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, checks before/after + one real thing, revert. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task_result> Changes: skills/task-abort-guard/references/pairs.json 12->17 (+ta-task-timeout, ta-write-receipt, ta-read-window, ta-edit-reread, ta-grep-scope, none deleted); SKILL.md version 1.1.0 + 5 rules; errors.md +5; pairs.md regenerated 17; sources.md bump note; proofs resealed. Proofs: run_task 17/17 PASS, lint 17 rules 728 tok PASS, sheet 12 PASS, grade 12 runs 1.0/0.0 lift 1.0 PASS, live_proof proven 6 passed, full suite 645 passed 3 failed out-of-scope (2 git-one-branch concurrent-tree + 1 seat-guard pre-land). Guards hold. Never committed. RESULT: DONE - task-abort-guard v1.1.0 12->17 pairs re-proved | proof: python tests/live_proof.py task-abort-guard -> proven 6 passed </task_result>

Keeper facts: run builder-cure-weakest13 (seat builder-cure, @builder), cure weakest installed bump r13.
RESULT: DONE - task-abort-guard v1.1.0 12->17 pairs re-proved | proof: python tests/live_proof.py task-abort-guard -> proven 6 passed
