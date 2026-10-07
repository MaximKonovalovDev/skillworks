---
role: judge
title: review read-abort-guard skill (a fleet failure to a proven skill)
chain: review
of: builder-cure-readabort
writer: builder
attempt: 1
origin_title: cure DR-1006-12 read-abort-guard skill
---
Review builder-cure-readabort, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-readabort.md. Rerun its proof yourself, read its diff, check its row DR-1006-12's done-when as written (partly is FAIL). You never edit.

Lead scoping (binding): F2P class-halving needs adoption plus the 48 h re-scan per the row; judge the trial proxy (runs with beat runs without by 0.3). Concurrent dirty files are out of scope — judge only skills/read-abort-guard/, evals/read-abort-guard_trials.jsonl, evals/read-abort-guard_qa.jsonl, tests/test_read_abort_guard.py, gates/install FLEET lines, THIRD_PARTY_NOTICES.md credit line.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters; (c) privacy: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved or the diff has a test that failed before and passes now. Moved nothing is FAIL "paperwork".

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, checks before/after + one real thing, revert. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task_result> Built the read-abort-guard slice: own-MIT manual + make receipts, then real skill SKILL.md (12 rules, 757 tok, every rule [src:]); 12 live pairs via scripts/run_read.py (12/12 PASS pwsh 7 scratch); pairs.md + errors.md + sources.md; test file; QA 10/10; trial grade 12 runs 1.0/0.0 lift 1.0; lint PASS; live_proof proven 6 passed; FLEET entries; THIRD_PARTY credit; p3 log. Guards held, no commits. Full pytest 640 passed, 1 pre-existing seat-guard FAIL (unlanded keeper-ready + this skill pending lead land, out of scope). RESULT: DONE - read-abort-guard skill built and proven (12 pairs, live 6, lint 12 rules, grade 1.0/0.0) | proof: python tests/live_proof.py read-abort-guard -> proven </task_result>

Keeper facts: run builder-cure-readabort (seat builder-cure, @builder), cure DR-1006-12 read-abort-guard skill.
RESULT: DONE - read-abort-guard skill built and proven | proof: python tests/live_proof.py read-abort-guard -> proven
