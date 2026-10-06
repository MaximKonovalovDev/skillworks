---
role: judge
title: review cure smith (a fleet failure to a proven skill) #7
chain: review
of: builder-cure-r7
writer: builder
attempt: 1
origin_title: cure smith (a fleet failure to a proven skill) #7
---
Review builder-cure-r7, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-r7.md. Rerun its proof yourself, read its diff, check its rows' done-when as written (partly is FAIL). You never edit.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` (or `python -m book2skill distill check --skill skills/<name>`) exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. A tool (`tools/`, `book2skill/`): its test, `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks`, the `sprint/steals.md` line says `landed <sha>`, and the first job's output exists (open it).
3. A pack (`packs/<slug>/`): `python tools/pack_check.py packs/<slug>` ends `RESULT PASS`; the licence line of every source matches `references/sources.md`; no NonCommercial source has a price.
4. An install: `python tools/install_fleet_skills.py --to C:/Users/me/.config/opencode/skills --check <name>` exit 0, `opencode debug skill --pure` lists it, the `adopted.csv` row has its before number.

Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters (2026-10-03 a nested export crashed the OpenCode server); (c) privacy of this public repo: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved (proven, trials, installed, loads, a class, tools landed) or the diff has a test that failed before and passes now. A result that moved nothing is FAIL "paperwork", even when every command is green.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task id="ses_eee077bb3ffeux8UWMmy4ZnGO4" state="completed"> <task_result> Goal: halve read-offset class (30 `Offset N is out of range` in 48 h) in repos that load the skill. Scope: `skills/read-offset-guard/`, `evals/`, `tests/`, `book2skill/gates.py` FLEET_SKILLS + `tools/install_fleet_skills.py` FLEET (both already list it, no change). Proof: red replay before — `Offset 60 is out of range for this file (3 lines)`; `live_proof` after — proven. Stop: L 45 min; version bump M 25 min. DR-1006-5 version bump done (claimed `DR-1006-5 | builder-cure-r7` in `sprint/queue/claims.txt`; steals: no open doctor line, all landed per brief). - Red replay first on a 3-line scratch file at offset 60: real error line `Offset 60 is out of range for this file (3 lines)` (matches newest DB hit 10-06T15:59Z). - Bumped `skills/read-offset-guard/SKILL.md:3-4` description to fire before reads ("Use when reading a file with offset and limit, and when a read call comes back...") + `version: 1.1.0`, added missing shrink-limit rule `skills/read-offset-guard/SKILL.md:30` (`[Math]::Min($l, $n - $o)` → `pairs.md#ro-queue32`). - Added 5 pairs from newest 48 h failures in `skills/read-offset-guard/references/pairs.json`: ro-deep44 (315/44), ro-queue32 (90/32), ro-index542 (600/542), ro-index541 (620/541), ro-handoff28 (30/28); no passing pair deleted. Regenerated `references/pairs.md`, extended `references/errors.md:17-21`, updated `references/sources.md:1-7` (MIT verified 2026-10-06, bump note, live replay 60/3). - Proofs: `run_offset.py` 17 of 17 PASS; `skill_lint.py check` RESULT PASS (13 rules, 636 tok); `skill_trial.py sheet` 12 tasks PASS + `grade` 12 runs 1.0/0.0 lift 1.0; `tests/test_read_offset_guard.py` 3 passed 3 skipped (live skipped); `live_proof.py read-offset-guard` proven 6 passed. Export guard clean (no `skills/**/export`, no path >240). Full `pytest tests/` 605 passed + 1 seat-guard FAIL from concurrent BK-1006-3 `gh-cli-manual` untracked files (out of scope, same as prior runs). Lanes refreshed; one line appended to `team/p3.md:39`. Never committed. RESULT: DONE - read-offset-guard proven v1.0.0 -> v1.1.0, 26 -> 26 no count bump | proof: python tests/live_proof.py read-offset-guard ends proven (6 passed in 2.60s) </task_result> </task>

Keeper facts: run builder-cure-r7 (seat builder-cure, @builder), cure smith (a fleet failure to a proven skill) #7.
RESULT: DONE - read-offset-guard proven v1.0.0 -> v1.1.0, 26 -> 26 no count bump | proof: python tests/live_proof.py read-offset-guard ends proven (6 passed in 2.60s)
