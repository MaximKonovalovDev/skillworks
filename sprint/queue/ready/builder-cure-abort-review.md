---
role: judge
title: review abort-guard bump (a fleet failure to a proven skill)
chain: review
of: builder-cure-abort
writer: builder
attempt: 1
origin_title: cure DR-1006-9 abort-guard version bump
---
Review builder-cure-abort, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-abort.md. Rerun its proof yourself, read its diff, check its row DR-1006-9's done-when as written (partly is FAIL). You never edit.

Lead scoping (binding): F2P class-halving needs adoption plus the 48 h re-scan per the row; judge the trial proxy (runs with beat runs without by 0.3). Concurrent dirty files are out of scope — judge only skills/bash-abort-guard/, evals/bash-abort-guard_trials.jsonl, tests/test_bash_abort_guard.py.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters; (c) privacy: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved or the diff has a test that failed before and passes now. Moved nothing is FAIL "paperwork".

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, checks before/after + one real thing, revert. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task_result> Red replay: scan `bash: Tool execution aborted` n=92; real line `RuntimeException: Tool execution aborted on bash cargo check --locked -p engine-game heavy build foreground`. Changes skills/bash-abort-guard/ only: SKILL.md version 1.1.0 + 6 rules; pairs.json 12 → 18 (+bb-wrapper, bb-halve, bb-unhook, bb-bounded, bb-shortloop, bb-scope); pairs.md regenerated 18; errors.md +6; trial arms 12 → 18. Proofs: run_abort 18/18; lint RESULT PASS 18 rules 742 tok; sheet 18 PASS; grade 18 runs 1.0/0.0 lift 1.0 PASS; live_proof proven 6 passed in 4.89s; pytest 612 passed 154 skipped 1 seat-guard concurrent out-of-scope. Guards hold. Never committed. RESULT: DONE - bash-abort-guard v1.0.0 → v1.1.0 proven (18/18 pairs PASS) | proof: python tests/live_proof.py bash-abort-guard ends proven </task_result>

Keeper facts: run builder-cure-abort (seat builder-cure, @builder), cure DR-1006-9 abort-guard version bump.
RESULT: DONE - bash-abort-guard v1.0.0 → v1.1.0 proven (18/18 pairs PASS) | proof: python tests/live_proof.py bash-abort-guard ends proven
