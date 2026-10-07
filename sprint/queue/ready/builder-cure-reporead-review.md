---
role: judge
title: review repo-read-first bump (a fleet failure to a proven skill)
chain: review
of: builder-cure-weakest12
writer: builder
attempt: 1
origin_title: cure weakest installed bump r12
---
Review builder-cure-weakest12, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-weakest12.md. Rerun its proof yourself, read its diff, check its row DR-1004-3's done-when as written (partly is FAIL). You never edit.

Lead scoping (binding): F2P class-halving needs adoption plus the 48 h re-scan per the row; judge the trial proxy (12 runs with beat 12 without by 0.3). Concurrent dirty files are out of scope — judge only skills/repo-read-first/, evals/repo-read-first_trials.jsonl, tests/test_repo_read_first.py.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters; (c) privacy: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved or the diff has a test that failed before and passes now. Moved nothing is FAIL "paperwork".

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, checks before/after + one real thing, revert. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task_result> Changes: skills/repo-read-first/references/pairs.json 12→17 (+rr-b07 timeout, rr-b08 branch, rr-b09 nested, rr-b10 third-repo, rr-b11 main-raw; none deleted); errors.md +5; pairs.md regenerated 17; SKILL.md version 1.0.0→1.1.0 + Fresh-shapes 5 rules; sources.md v1.1.0 note; proofs resealed. Red replay: Repository not found / does not point to a file / 404 bare throws live in pwsh. Proof: live_proof proven 6 passed in 2.40s; lint RESULT PASS 17 rules 810 tok; grade 12 runs 0.9167/0.0 lift 0.9167 RESULT PASS; pytest 640 passed 1 pre-existing seat-guard FAIL concurrent out-of-scope. RESULT: DONE - repo-read-first v1.0.0->v1.1.0 proven 12->17 pairs, all green | proof: python tests/live_proof.py repo-read-first -> proven (6 passed in 2.40s) </task_result>

Keeper facts: run builder-cure-weakest12 (seat builder-cure, @builder), cure weakest installed bump r12.
RESULT: DONE - repo-read-first v1.0.0->v1.1.0 proven 12->17 pairs, all green | proof: python tests/live_proof.py repo-read-first -> proven (6 passed in 2.40s)
