---
role: judge
title: review score-risk build plus wire
chain: review
of: builder-cure-scorerisk-finish
writer: builder
attempt: 1
origin_title: cure judge score-risk lines (S50 trial)
---
Review builder-cure-scorerisk-finish (plus its base builder-cure-scorerisk), built by builder. Records: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-scorerisk-finish.md and C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-scorerisk.md (if the base record is missing, judge the tree for the base and say so). Rerun the proofs yourself, read the diff, check DR-1007-4's done-when as written. You never edit.

Rerun and paste each result line: `python tests/live_proof.py judge-score-risk` ends proven; lint exit 0 (10 or more pairs, body at most 2000 tokens, ASCII); grade 12 runs with/without plus lift; `node sprint/check.mjs` PASS.

Always: (a) pytest plus check equal or better than before (pre-existing out-of-scope fails named, not charged); (b) nesting guard clean; (c) privacy clean; (d) only owned files changed (skill, sheet, test, 4 wire lines, credit); no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Finish result, cut:
<task_result> RESULT: DONE - wired judge-score-risk into the fleet: FLEET_SKILLS line book2skill/gates.py, FLEET name tools/install_fleet_skills.py, MIT original-work credit THIRD_PARTY_NOTICES.md, tried line team/p3.md; skill bodies untouched, proofs resealed (live-proof same fingerprint, date 06:05Z) | proof: python tests/live_proof.py judge-score-risk -> proven 6 passed in 7.35s; grade 12 runs 1.0/0.0 lift 1.0 PASS; check.mjs 20/0/0 </task_result>

Keeper facts: run builder-cure-scorerisk-finish (seat builder, @builder), finish judge-score-risk wire plus re-proof.
