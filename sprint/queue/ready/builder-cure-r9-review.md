---
role: judge
title: review read-offset bump (a fleet failure to a proven skill) #9
chain: review
of: builder-cure-r9
writer: builder
attempt: 1
origin_title: cure smith (a fleet failure to a proven skill) #9
---
Review builder-cure-r9, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-r9.md. Rerun its proof yourself, read its diff, check its row DR-1006-5's done-when as written (partly is FAIL). You never edit.

Lead scoping (binding): F2P class-halving needs adoption plus the 48 h re-scan per the row itself; judge the trial proxy (12 runs with beat 12 without by 0.3) plus whether the skill is installed and measurable. Concurrent dirty files are out of scope — judge only the skill files below.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` (or `python -m book2skill distill check --skill skills/<name>`) exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters (2026-10-03 a nested export crashed the OpenCode server); (c) privacy of this public repo: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved (proven, trials, installed, loads, a class, tools landed) or the diff has a test that failed before and passes now. A result that moved nothing is FAIL "paperwork", even when every command is green.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task_result> Goal: cure DR-1006-5 read-offset-guard version bump. Red: `Offset 60 is out of range for this file (3 lines)` on 3-line scratch at offset 60. Changes: pairs.json 17 -> 22 (+ro-board180, ro-index544, ro-empty0, ro-handoff135, ro-index534 from newest scan 33 in 48h); pairs.md regenerated 22 pairs; errors.md +5 fragments; SKILL.md version 1.1.0 -> 1.2.0 +5 rules (18 rules 816 tok); sources.md scan note; live-proof fp 25a8849c 6 passed. Proof: run_offset 22/22 PASS, lint 18 rules 816 tok RESULT PASS, sheet 12 RESULT PASS, grade 12 runs 1.0/0.0 lift 1.0 PASS, live 6 passed proven, suite 605 passed 1 seat-guard FAIL concurrent out-of-scope, export guard clean, lanes refreshed. RESULT: DONE - read-offset-guard v1.1.0 -> v1.2.0 proven 26 -> 26 (22/22 pairs PASS) | proof: python tests/live_proof.py read-offset-guard ends proven </task_result>

Keeper facts: run builder-cure-r9 (seat builder-cure, @builder), cure smith (a fleet failure to a proven skill) #9.
RESULT: DONE - read-offset-guard v1.1.0 -> v1.2.0 proven 26 -> 26 (22/22 pairs PASS) | proof: python tests/live_proof.py read-offset-guard ends proven
