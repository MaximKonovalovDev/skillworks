---
role: judge
title: verdict on task-scope v1.2.0 re-proof
chain: review
of: 373-cure-taskscope-retry
writer: builder
attempt: 1
origin_title: cure task-scope retry for DR-1006-2
---
Review builder-cure retry, built by builder. Its record: C:\empire\skillworks\sprint\queue\claims.txt line `DR-1006-2 | builder-cure | 2026-10-09T10:16Z` reused by the retry (no done file; judge the tree and say so). Re-proof, not a bump: newest 42 Task-cancelled are shapes v1.2.0 already covers, 22/22 pairs PASS, proofs resealed with same fingerprints. Rerun its proof yourself, read its diff, check DR-1006-2's done-when as written (12 trial runs with beat 12 without by 0.3; suite equal or better; partly is FAIL). You never edit.

Run the skill checks and paste each result line: `python tests/live_proof.py task-scope` ends proven (builder: 6 passed); lint exit 0 (builder: 22 rules 960 tok); red replay bare Task-cancelled throws vs with-skill retry-lane PASS, outputs pasted; `python tools/skill_trial.py grade --skill task-scope` runs with/without plus lift (builder: 12 runs 1.0/0.0 lift 1.0); `node sprint/check.mjs` PASS. FLEET wire must be present or FAIL naming exactly that gap.

Always: (a) full pytest equal or better than the standing baseline (builder ran focused only per the light box; run what you need and name every FAILED line, charging only what traces to this diff; known standing fails: export-guard, c02, stale proofs, cli.py collectors); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed (skills/task-scope/references/, team/p3.md); no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Halving note: compare reads before 0 now 307 UP; halving needs adoption plus 48 h and cannot pass same-day. Name whether you PASS on shape or FAIL on unmet halving; partly is FAIL.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
