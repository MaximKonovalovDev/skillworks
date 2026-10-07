---
role: judge
title: review scout next book slice (book lane)
chain: review
of: researcher-books-scout
writer: researcher
attempt: 1
origin_title: scout next book slice (book lane)
---
Review researcher-books-scout, built by researcher. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\researcher-books-scout.md. Rerun its proof yourself, read its diff, check its rows' done-when as written (partly is FAIL). You never edit.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` (or `python -m book2skill distill check --skill skills/<name>`) exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. A tool (`tools/`, `book2skill/`): its test, `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks`, the `sprint/steals.md` line says `landed <sha>`, and the first job's output exists (open it).
3. A pack (`packs/<slug>/`): `python tools/pack_check.py packs/<slug>` ends `RESULT PASS`; the licence line of every source matches `references/sources.md`; no NonCommercial source has a price.
4. An install: `python tools/install_fleet_skills.py --to C:/Users/me/.config/opencode/skills --check <name>` exit 0, `opencode debug skill --pure` lists it, the `adopted.csv` row has its before number.

Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters (2026-10-03 a nested export crashed the OpenCode server); (c) privacy of this public repo: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved (proven, trials, installed, loads, a class, tools landed) or the diff has a test that failed before and passes now. A result that moved nothing is FAIL "paperwork", even when every command is green.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task id="ses_ee8b33344ffeRC2d0hd0gePMBh" state="completed"> <task_result> Scout packet complete. Claim filed first, licence read live via repo record (kislyuk/yq Apache-2.0; jqlang/jq rejected as NOASSERTION), 2 sources into git-ignored work/yq-jq/src/, 12-task sheet plus with/without arms grading 1.0/0.0 lift 1.0, READY row BK-1007-5 appended, check green. RESULT: DONE - BK-1007-5 READY yq-jq row plus evals/yq-jq_trials.jsonl 12 tasks plus work/yq-jq/src 2 files | proof: grade runs 12 with_rate 1.0 without_rate 0.0 lift 1.0 RESULT PASS, rg exits 0 0 0 0, node sprint/check.mjs RESULT PASS 20 pass 0 warn 0 fail </task_result> </task>

Keeper facts: run researcher-books-scout (@researcher), scout next book slice (book lane).
RESULT: DONE - BK-1007-5 READY yq-jq row plus evals/yq-jq_trials.jsonl 12 tasks plus work/yq-jq/src 2 files | proof: grade runs 12 with_rate 1.0 without_rate 0.0 lift 1.0 RESULT PASS, rg exits 0 0 0 0, node sprint/check.mjs RESULT PASS 20 pass 0 warn 0 fail
