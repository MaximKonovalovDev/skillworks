---
role: judge
title: review websearch-retry new skill (a fleet failure to a proven skill)
chain: review
of: builder-cure-websearch
writer: builder
attempt: 1
origin_title: cure DR-1006-7 websearch-retry new skill
---
Review builder-cure-websearch, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-websearch.md. Rerun its proof yourself, read its diff, check its row DR-1006-7's done-when as written (partly is FAIL). You never edit.

Lead scoping (binding): F2P class-halving needs adoption plus the 48 h re-scan per the row; judge the trial proxy (12 runs with beat 12 without by 0.3). Concurrent dirty files are out of scope — judge only skills/websearch-retry/, evals/websearch-retry_trials.jsonl, evals/websearch-retry_qa.jsonl, tests/test_websearch_retry.py, book2skill/gates.py FLEET_SKILLS line, tools/install_fleet_skills.py FLEET line, THIRD_PARTY_NOTICES.md credit line.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters; (c) privacy: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved or the diff has a test that failed before and passes now. Moved nothing is FAIL "paperwork".

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, checks before/after + one real thing, revert. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task_result> Built skills/websearch-retry/ new skill (12 rules 640 tok, every rule ends [src:]); pairs 12 (busy/shape/timeout); runner scripts run_search plus pairs_to_md (scratch only); pairs.md generated, errors 12 fragments, sources own-MIT verified 2026-10-06; evals QA 10 rows 10/10 rate 1.0; trial sheet 12 PASS, grade 12 runs 1.0/0.0 lift 1.0 PASS; live_proof proven 6 passed; targeted 140 passed; full suite 612 passed + 1 seat-guard FAIL pre-land untracked (lead lands) + 1 concurrent repomap out-of-scope. Guards hold. RESULT: DONE - websearch-retry skill built, proven, lint/trial/live green | proof: python tests/live_proof.py websearch-retry -> proven 6 passed; grade 12 runs 1.0/0.0 lift 1.0 </task_result>

Keeper facts: run builder-cure-websearch (seat builder-cure, @builder), cure DR-1006-7 websearch-retry new skill.
RESULT: DONE - websearch-retry skill built, proven, lint/trial/live green | proof: python tests/live_proof.py websearch-retry -> proven 6 passed; grade 12 runs 1.0/0.0 lift 1.0
