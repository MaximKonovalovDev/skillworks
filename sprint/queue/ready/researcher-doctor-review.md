---
role: judge
title: review skill doctor (fleet failures to a red test and a brief)
chain: review
of: researcher-doctor
writer: researcher
attempt: 1
origin_title: skill doctor (fleet failures to a red test and a brief)
---
Review researcher-doctor, built by researcher. Its record: C:\empire\skillworks\sprint\queue\done\researcher-doctor.md. Rerun its proof yourself, read its diff, check its rows' done-when as written (partly is FAIL). You never edit.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` (or `python -m book2skill distill check --skill skills/<name>`) exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. A tool (`tools/`, `book2skill/`): its test, `node C:/empire/center/arsenal.mjs --check skillworks`, the `sprint/steals.md` line says `landed <sha>`, and the first job's output exists (open it).
3. A pack (`packs/<slug>/`): `python tools/pack_check.py packs/<slug>` ends `RESULT PASS`; the licence line of every source matches `references/sources.md`; no NonCommercial source has a price.
4. An install: `python tools/install_fleet_skills.py --to C:/Users/me/.config/opencode/skills --check <name>` exit 0, `opencode debug skill --pure` lists it, the `adopted.csv` row has its before number.

Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters (2026-10-03 a nested export crashed the OpenCode server); (c) privacy of this public repo: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved (proven, trials, installed, loads, a class, tools landed) or the diff has a test that failed before and passes now. A result that moved nothing is FAIL "paperwork", even when every command is green.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task id="ses_ee3dd7252ffemj9Vg9lqjtnhPC" state="completed"> <task_result> RESULT: DONE - DR-1007-21 READY task-subagent-guard 34 in 48 h plus evals/task-subagent-1007_trials.jsonl 12 run tasks | proof: sheet tasks 12 run 12 PASS plus node sprint/check.mjs RESULT PASS 20 pass plus scan generatedAt 2026-10-08T15:47Z </task_result> </task>

Keeper facts: run researcher-doctor (@researcher), skill doctor (fleet failures to a red test and a brief).
RESULT: DONE - DR-1007-21 READY task-subagent-guard 34 in 48 h plus evals/task-subagent-1007_trials.jsonl 12 run tasks | proof: sheet tasks 12 run 12 PASS plus node sprint/check.mjs RESULT PASS 20 pass plus scan generatedAt 2026-10-08T15:47Z
