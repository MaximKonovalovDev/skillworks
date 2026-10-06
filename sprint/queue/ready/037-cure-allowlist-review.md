---
role: judge
title: review allowlist bump (a fleet failure to a proven skill) #8
chain: review
of: builder-cure-r8
writer: builder
attempt: 1
origin_title: cure smith (a fleet failure to a proven skill) #8
---
Review builder-cure-r8, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-r8.md. Rerun its proof yourself, read its diff, check its row DR-1006-6's done-when as written (partly is FAIL). You never edit.

Goal: judge the allowlist v1.0.0 -> v1.1.0 bump (5 new pairs, 12 -> 17). Scope: skills/bash-allowlist/, evals/bash-allowlist_trials.jsonl, tests/test_bash_allowlist.py, team/p3.md line. Proof: live_proof proven + lint PASS + grade 1.0/0.0 lift 1.0 + red replay failed-before passes-now. Stop: 15 lines, VERDICT only.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` (or `python -m book2skill distill check --skill skills/<name>`) exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. A tool (`tools/`, `book2skill/`): its test, `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks`, the `sprint/steals.md` line says `landed <sha>`, and the first job's output exists (open it).
3. A pack (`packs/<slug>/`): `python tools/pack_check.py packs/<slug>` ends `RESULT PASS`; the licence line of every source matches `references/sources.md`; no NonCommercial source has a price.
4. An install: `python tools/install_fleet_skills.py --to C:/Users/me/.config/opencode/skills --check <name>` exit 0, `opencode debug skill --pure` lists it, the `adopted.csv` row has its before number.

Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters (2026-10-03 a nested export crashed the OpenCode server); (c) privacy of this public repo: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved (proven, trials, installed, loads, a class, tools landed) or the diff has a test that failed before and passes now. A result that moved nothing is FAIL "paperwork", even when every command is green.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task_result> Built v1.0.0 -> v1.1.0 (never deleted a passing pair, 12 -> 17): SKILL.md version 1.1.0 plus 5 fresh-shape rules with [src:]; pairs.json 12 -> 17 (ba-nested, ba-blocked, ba-sleep, ba-inline, ba-lanes), run_allow.py 17 of 17 PASS; errors.md 5 new Pair lines; sources.md verified 2026-10-06 MIT; trial-proof re-proved grade runs 12 with_rate 1.0 without_rate 0.0 lift 1.0 RESULT PASS; live-proof proven 6 passed in 14.60s; skill_lint RESULT PASS 17 rules 725 tok; test_bash_allowlist 3 passed; sheet 12 RESULT PASS; pytest 606 passed 150 skipped. Guards hold. RESULT: DONE - bash-allowlist v1.0.0->v1.1.0 proven 26->26 | proof: python tests/live_proof.py bash-allowlist ends proven (6 passed in 14.60s) </task_result>

Keeper facts: run builder-cure-r8 (seat builder-cure, @builder), cure smith (a fleet failure to a proven skill) #8.
RESULT: DONE - bash-allowlist v1.0.0->v1.1.0 proven 26->26 | proof: python tests/live_proof.py bash-allowlist ends proven (6 passed in 14.60s)
