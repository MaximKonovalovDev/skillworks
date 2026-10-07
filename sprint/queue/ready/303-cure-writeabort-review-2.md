---
role: judge
title: review cure write-abort class (DR-1007-12)
chain: review
of: 303-cure-writeabort
writer: builder
attempt: 2
origin_title: cure write-abort class (DR-1007-12)
---
Review 303-cure-writeabort, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\303-cure-writeabort-repair.md. Rerun its proof yourself, read its diff, check its rows' done-when as written (partly is FAIL). You never edit.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` (or `python -m book2skill distill check --skill skills/<name>`) exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. A tool (`tools/`, `book2skill/`): its test, `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks`, the `sprint/steals.md` line says `landed <sha>`, and the first job's output exists (open it).
3. A pack (`packs/<slug>/`): `python tools/pack_check.py packs/<slug>` ends `RESULT PASS`; the licence line of every source matches `references/sources.md`; no NonCommercial source has a price.
4. An install: `python tools/install_fleet_skills.py --to C:/Users/me/.config/opencode/skills --check <name>` exit 0, `opencode debug skill --pure` lists it, the `adopted.csv` row has its before number.

Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters (2026-10-03 a nested export crashed the OpenCode server); (c) privacy of this public repo: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved (proven, trials, installed, loads, a class, tools landed) or the diff has a test that failed before and passes now. A result that moved nothing is FAIL "paperwork", even when every command is green.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task id="ses_ee83daee0ffeQJec0q1FaRaHKO" state="completed"> <task_result> Repaired the verdict's failing check: `write-abort-guard` was built but never registered, so `live_proof.py` rejected it as unknown. - `book2skill/gates.py:71` added `"write-abort-guard": [],` (original work, no credit needle, matching read/edit-abort-guard). - `evals/write-abort-guard_qa.jsonl:1-10` new QA (10 rows mirroring read/edit-abort pattern, all must-words in skill text) so the new fleet registration passes the eval gate (rate 1.0). - `skills/write-abort-guard/references/live-proof.json` re-proven with the new fingerprint (was stale once QA joined the fingerprint). Red replay (rerunnable): `python skills/write-abort-guard/scripts/run_write.py` → 12 of 12 PASS; wa-slice bad fails with `Tool execution aborted: whole write in one call`, good passes printing `slice chunk timeout PASS 1-5`. Lint RESULT PASS (12 rules/24 pairs/763 tokens); grade 12 runs 1.0/0.0 lift 1.0; fleet `-k write-abort-guard` 4 passed; `node sprint/check.mjs` RESULT PASS 20/0/0; full pytest 6 failed/747 passed/211 skipped — same 6 pre-existing out-of-scope fails (bash-spawn pairs_md, c02 golden, engine-builder rule source, bash-spawn/engine-builder live-proofs, seat untracked), +4 passed vs verdict's 743. RESULT: DONE - registered write-abort-guard in FLEET_SKILLS with QA so live_proof ends proven | proof: `python tests/live_proof.py write-abort-guard` -> write-abort-guard: proven. 6 passed in 11.78s </task_result> </task>

Keeper facts: run 303-cure-writeabort-repair (@builder), repair cure write-abort class (DR-1007-12).
RESULT: DONE - registered write-abort-guard in FLEET_SKILLS with QA so live_proof ends proven | proof: `python tests/live_proof.py write-abort-guard` -> write-abort-guard: proven. 6 passed in 11.78s
