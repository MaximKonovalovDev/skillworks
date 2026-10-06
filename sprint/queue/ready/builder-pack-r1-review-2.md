---
role: judge
title: review pack maker (tested skills to a sellable pack for the factory) #1
chain: review
of: builder-pack-r1
writer: builder
attempt: 2
origin_title: pack maker (tested skills to a sellable pack for the factory) #1
---
Review builder-pack-r1, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-pack-r1-repair.md. Rerun its proof yourself, read its diff, check its rows' done-when as written (partly is FAIL). You never edit.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` (or `python -m book2skill distill check --skill skills/<name>`) exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. A tool (`tools/`, `book2skill/`): its test, `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks`, the `sprint/steals.md` line says `landed <sha>`, and the first job's output exists (open it).
3. A pack (`packs/<slug>/`): `python tools/pack_check.py packs/<slug>` ends `RESULT PASS`; the licence line of every source matches `references/sources.md`; no NonCommercial source has a price.
4. An install: `python tools/install_fleet_skills.py --to C:/Users/me/.config/opencode/skills --check <name>` exit 0, `opencode debug skill --pure` lists it, the `adopted.csv` row has its before number.

Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters (2026-10-03 a nested export crashed the OpenCode server); (c) privacy of this public repo: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved (proven, trials, installed, loads, a class, tools landed) or the diff has a test that failed before and passes now. A result that moved nothing is FAIL "paperwork", even when every command is green.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task id="ses_ef0b3db2effeG4aY41sDiskrQ8" state="completed"> <task_result> Fixed the verdict's 3–5 gate findings with one repair: proof dates + stale zip. RESULT: DONE - packs/fleet-vol-1/listing.md:98-100 proof dates 2026-10-05→2026-10-06 (7/11/42 passed), dist zips rebuilt via pack_build | proof: `python tools/pack_check.py packs/fleet-vol-1` → RESULT PASS: fleet-vol-1 (13 checks pass, 0 warnings, 0 store assets still needed before it can go live) </task_result> </task>

Keeper facts: run builder-pack-r1-repair (@builder), repair pack maker (tested skills to a sellable pack for the factory) #1.
RESULT: DONE - packs/fleet-vol-1/listing.md:98-100 proof dates 2026-10-05→2026-10-06 (7/11/42 passed), dist zips rebuilt via pack_build | proof: `python tools/pack_check.py packs/fleet-vol-1` → RESULT PASS: fleet-vol-1 (13 checks pass, 0 warnings, 0 store assets still needed before it can go live)
