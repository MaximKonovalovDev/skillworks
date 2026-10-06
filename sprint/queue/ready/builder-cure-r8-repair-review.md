---
role: judge
title: review allowlist repair (a fleet failure to a proven skill) #8
chain: review
of: builder-cure-r8-repair
writer: builder
attempt: 1
origin_title: repair allowlist bump (a fleet failure to a proven skill) #8
---
Review builder-cure-r8-repair, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-r8-repair.md. Rerun its proof yourself, read its diff, check its row DR-1006-6's done-when as written (partly is FAIL). You never edit.

Lead scoping (binding): F2P class-halving needs adoption plus the 48 h re-scan per the row; judge the trial proxy (runs with beat runs without by 0.3). Concurrent dirty files are out of scope — judge only skills/bash-allowlist/, evals/bash-allowlist_trials.jsonl, tests/test_bash_allowlist.py.

Run the check that fits what it made, and paste the result line of each:
1. A skill (`skills/<name>/`): `python tests/live_proof.py <name>` ends `proven`; `python tools/skill_lint.py <name>` exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs or trials, no scaffold text, ASCII); then 3 of its sample bad cases run once with and once without the skill, outputs pasted. The packet's red replay must have failed before and pass now.
2. Always, for every result: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before; (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters; (c) privacy: `git diff` has no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA to make a rate pass; (e) ONE REAL THING: `python tools/fleet_failures.py round-line --check` shows a number that moved or the diff has a test that failed before and passes now. Moved nothing is FAIL "paperwork".

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, checks before/after + one real thing, revert. A proof you cannot run is BLOCKED, never a guess.

Its result, cut:
<task_result> Repair done. Trials ADD not swap: restored ba-b01..b06 byte-identical plus ba-g01..g06 untouched; kept ba-b07/08/09/11, rewrote ba-b10 to lanes shape, dropped redundant ba-b12. Diff vs HEAD exactly +5 lines, 17 tasks. Red replay auditable: live pwsh replay of ba-nested/ba-sleep/ba-lanes, record at work/trials/bash-allowlist/red-green.txt (git-ignored), pasted red exit 1 policy line plus green exit 0. Proofs: grade 17 runs 1.0/0.0 lift 1.0 PASS (trial-proof resealed fp 0b0ebcac); lint 17 rules 725 tok PASS; pytest test_bash_allowlist 6 passed; live_proof proven 6 passed; check 20/0/0 PASS; full pytest 605 passed 1 seat-guard FAIL concurrent out-of-scope. Nothing committed. RESULT: DONE | proof: python tools/skill_trial.py grade --skill bash-allowlist → runs 17, with_rate 1.0, without_rate 0.0, lift 1.0 RESULT PASS </task_result>

Keeper facts: run builder-cure-r8-repair (@builder), repair allowlist bump #8.
RESULT: DONE | proof: python tools/skill_trial.py grade --skill bash-allowlist → runs 17, with_rate 1.0, without_rate 0.0, lift 1.0 RESULT PASS
