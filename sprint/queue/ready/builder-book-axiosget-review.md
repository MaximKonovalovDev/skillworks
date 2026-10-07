---
role: judge
title: review axios-get build (judge the tree)
chain: review
of: builder-book-axiosget
writer: builder
attempt: 1
origin_title: build axios-get skill (book slice to proven skill)
---
Review builder-book-axiosget, built by builder. No done record was written, so judge the worktree diff directly against BK-1007-2's done-when (grade with_rate 0.8 or more and lift 0.3 or more; pytest green; check PASS). You never edit.

Rerun the proofs yourself and paste each result line:
1. A skill: `python tests/live_proof.py axios-get` ends `proven` (if unknown-skill, the FLEET wire is missing: rule FAIL naming exactly that gap, nothing else). Distill or lint check exit 0 (10 or more pairs, body at most 2000 tokens, ASCII). Grade rerun with/without numbers pasted.
2. Licence: every source line matches references/sources.md (MIT only, no NonCommercial, no price); sources stayed in work/ ignored.

Always: (a) pytest plus check equal or better than before (pre-existing out-of-scope fails named, not charged); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed (skills/axios-get/, evals sheets, its test); no weakened gate, no edited QA; (e) ONE REAL THING: grade lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Built result, cut:
<task_result> RESULT: DONE - built skills/axios-get/ (SKILL.md:8 rules/799 tok + sources/glossary/patterns/cheatsheet + trial-proof + live-proof) and tests/test_axios_get.py, trials sheet untouched, nothing committed | proof: lint RESULT PASS (pairs 12, body 799), grade runs 12 with_rate 1.0 lift 1.0, SKILL_LIVE pytest 11 passed, full suite 662 passed with only the 5 pre-existing failures proven identical on hold-out baseline, check.mjs 20/0/0 </task_result>

Keeper facts: run builder-book-axiosget (seat builder, @builder), build axios-get skill. No done record; judging the tree.
