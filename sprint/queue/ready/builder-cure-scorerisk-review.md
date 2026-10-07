---
role: judge
title: review judge-score-risk cure
chain: review
of: builder-cure-scorerisk
writer: builder
attempt: 1
origin_title: cure judge score-risk lines (S50 trial)
---
Review builder-cure-scorerisk, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-scorerisk.md (if missing, judge the tree and say so). Rerun the proofs yourself, read the diff, check DR-1007-4's done-when as written (trial proxy: 12 runs with beat 12 without by 0.3; suite equal or better). You never edit.

Rerun and paste each result line: red replay (one case of the class fails before, passes now, with and without outputs pasted); `python tests/live_proof.py judge-score-risk` ends proven; lint check exit 0 (10 or more pairs, body at most 2000 tokens, ASCII); grade 12 runs with/without plus lift; `node sprint/check.mjs` PASS.

Always: (a) full pytest equal or better than before (pre-existing out-of-scope fails named, not charged); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Built result, cut:
<task_result> RESULT: DONE - new skill judge-score-risk (12 pairs, scored YAML verdict for judge read-missing class) with trial-proof lift 1.0 and live 6 passed | proof: python tools/skill_lint.py check --skill skills/judge-score-risk -> RESULT PASS exit 0; grade 12 runs 1.0/0.0 lift 1.0; pytest 694 passed + same 2 pre-existing fails; check.mjs 20/0/0 </task_result>

Keeper facts: run builder-cure-scorerisk (seat builder, @builder), cure judge score-risk lines.
