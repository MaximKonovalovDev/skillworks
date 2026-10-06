---
role: judge
title: review edit-verify bump (a fleet failure to a proven skill) #10
chain: review
of: builder-cure-r10
writer: builder
attempt: 1
origin_title: cure smith (a fleet failure to a proven skill) #10
---
Review builder-cure-r10, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-r10.md. Rerun its proof yourself, read its diff, check its row DR-1006-4's done-when as written (partly is FAIL). You never edit.

Lead scoping (binding): F2P class-halving needs adoption plus the 48 h re-scan per the row; judge the trial proxy (12 runs with beat 12 without by 0.3). Concurrent dirty files are out of scope — judge only skills/edit-verify/, evals/edit-verify_trials.jsonl, tests/test_edit_verify.py.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters; (c) privacy: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved or the diff has a test that failed before and passes now. Moved nothing is FAIL "paperwork".

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, checks before/after + one real thing, revert. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task_result> Goal version-bump edit-verify DR-1006-4 v0.1.0→v0.2.0 (+5 fresh-shape pairs, re-prove). Red replay: `Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.` Changes: SKILL.md version 0.2.0 +5 rules (ev-tabs/trail/stale/widen/case); pairs.json 12→17, none deleted; errors.md 5 rows; pairs.md regenerated 17; team/p3.md one line. Guards hold. RESULT: DONE - edit-verify v0.2.0 bump with 5 new pairs, all proofs green | proof: python tests/live_proof.py edit-verify → proven 6 passed; lint ok true 17 rules 816 tok; grade 12 runs 1.0/0.0 lift 1.0; pytest 605 passed 1 seat-guard FAIL concurrent out-of-scope </task_result>

Keeper facts: run builder-cure-r10 (seat builder-cure, @builder), cure smith (a fleet failure to a proven skill) #10.
RESULT: DONE - edit-verify v0.2.0 bump with 5 new pairs, all proofs green | proof: python tests/live_proof.py edit-verify → proven 6 passed
