---
role: judge
title: review edit-identical new skill (a fleet failure to a proven skill)
chain: review
of: builder-cure-identical
writer: builder
attempt: 1
origin_title: cure DR-1006-10 edit-identical new skill
---
Review builder-cure-identical, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-identical.md. Rerun its proof yourself, read its diff, check its row DR-1006-10's done-when as written (partly is FAIL). You never edit.

Lead scoping (binding): F2P class-halving needs adoption plus the 48 h re-scan per the row; judge the trial proxy (12 runs with beat 12 without by 0.3). Concurrent dirty files are out of scope — judge only skills/edit-identical/, evals/edit-identical_trials.jsonl, evals/edit-identical_qa.jsonl, tests/test_edit_identical.py, gates/install FLEET lines, THIRD_PARTY_NOTICES.md credit line.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters; (c) privacy: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved or the diff has a test that failed before and passes now. Moved nothing is FAIL "paperwork".

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, checks before/after + one real thing, revert. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task_result> Built skills/edit-identical/: SKILL.md 12 rules 763 tok every rule ends [src:]; pairs.json 12 pairs 12/12 PASS pwsh 7; pairs.md/errors.md/sources.md (MIT verified 2026-10-06); scripts run_identical plus pairs_to_md; evals/edit-identical_qa.jsonl 10 rows eval 1.0; tests/test_edit_identical.py 3 passed 6 live passed; FLEET lists wired; THIRD_PARTY credit; claims plus p3 lines. Guards hold. Never committed. Lanes refreshed. RESULT: DONE - edit-identical proven 27->28 pending land (12/12 pairs, live 6, lint 12 rules 763 tok, grade 12 runs 1.0/0.0 lift 1.0) | proof: python tests/live_proof.py edit-identical ends proven (6 passed in 2.16s) </task_result>

Keeper facts: run builder-cure-identical (seat builder-cure, @builder), cure DR-1006-10 edit-identical new skill.
RESULT: DONE - edit-identical proven 27->28 pending land | proof: python tests/live_proof.py edit-identical ends proven (6 passed in 2.16s)
