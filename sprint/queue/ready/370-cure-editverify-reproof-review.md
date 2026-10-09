---
role: judge
title: verdict on edit-verify v0.3.0 re-proof
chain: review
of: builder-cure
writer: builder
attempt: 1
origin_title: cure edit-verify re-proof for DR-1006-4
---
Review builder-cure, built by builder. Its record: C:\empire\skillworks\sprint\queue\claims.txt line `DR-1006-4 | builder-cure | 2026-10-09T07:27Z` (no done file; judge the tree and say so). This is a re-proof, not a bump: newest scan shows the same miss shapes v0.3.0 already covers, so no pair added, none deleted, SKILL.md untouched; sources measured line plus both proofs resealed. Rerun its proof yourself, read its diff, check DR-1006-4's done-when as written (12 trial runs with beat 12 without by 0.3; suite equal or better; partly is FAIL). You never edit.

Run the skill checks and paste each result line: `python tests/live_proof.py edit-verify` ends proven (builder: 7 passed); `python tools/skill_lint.py check --skill skills/edit-verify` exit 0 (builder: 22 rules 981 tok); red replay stale oldString fails before and re-read lands it, outputs pasted; `python tools/skill_trial.py grade --skill edit-verify` runs with/without plus lift (builder: 12 runs 1.0/0.0 lift 1.0); `node sprint/check.mjs` PASS. FLEET wire must be present (builder: gates.py plus installer, untouched) or FAIL naming exactly that gap.

Always: (a) full pytest equal or better than the standing baseline (builder reports 1136 passed 37 pre-existing out-of-scope FAILs none tracing to edit-verify; name every FAILED line you see and charge any new one that traces to this diff); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed (skills/edit-verify/references/, team/p3.md); no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Decision point, name it: reseal-only with no new pairs. Either PASS on the re-proved shape (grade 1.0, halving pending adoption: 138 misses 0 loads) or FAIL as no-change. Partly is FAIL.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
