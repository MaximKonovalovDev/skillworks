---
role: judge
title: review spawn bump (a fleet failure to a proven skill) #11
chain: review
of: builder-cure-r11
writer: builder
attempt: 1
origin_title: cure smith (a fleet failure to a proven skill) #11
---
Review builder-cure-r11, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-r11.md. Rerun its proof yourself, read its diff, check its row DR-1006-3's done-when as written (partly is FAIL). You never edit.

Lead scoping (binding): F2P class-halving needs adoption plus the 48 h re-scan per the row; judge the trial proxy (12 runs with beat 12 without by 0.3). Concurrent dirty files are out of scope — judge only skills/bash-spawn-guard/, evals/bash-spawn-guard_trials.jsonl, tests/test_bash_spawn_guard.py.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters; (c) privacy: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved or the diff has a test that failed before and passes now. Moved nothing is FAIL "paperwork".

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, checks before/after + one real thing, revert. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task_result> RESULT: DONE - DR-1006-3 bash-spawn-guard v1.2.0->v1.3.0 (22->27 pairs, 5 new gitstat/pytest/npminstall/logpoll/longpipe, no passing pair deleted); bad replay `RuntimeException: Unknown: ChildProcess.kill on detached check with no receipt to poll` | proof: python tests/live_proof.py bash-spawn-guard ends proven (9 passed in 5.91s), lint RESULT PASS (27 rules 1093 tok), trial sheet 12 tasks RESULT PASS + grade 12 runs 1.0/0.0 lift 1.0, pytest 605 passed 1 seat-guard FAIL out-of-scope (concurrent websearch-retry untracked, untouched) </task_result>

Keeper facts: run builder-cure-r11 (seat builder-cure, @builder), cure smith (a fleet failure to a proven skill) #11.
RESULT: DONE - DR-1006-3 bash-spawn-guard v1.2.0->v1.3.0 (22->27 pairs) | proof: python tests/live_proof.py bash-spawn-guard ends proven (9 passed in 5.91s)
