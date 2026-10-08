---
role: judge
title: review repro-first cure
chain: review
of: builder-cure-reprofirst
writer: builder
attempt: 1
origin_title: cure repro-first gate (S50 trial)
---
Review builder-cure-reprofirst, built by builder. Its record: C:\empire\skillworks\sprint\queue\done\builder-cure-reprofirst.md (if missing, judge the tree and say so). Rerun the proofs yourself, read the diff, check DR-1007-5's done-when as written (trial proxy: 12 runs with beat 12 without by 0.3; suite equal or better). You never edit.

Rerun and paste each result line: red replay (one aborted-task case fails before, passes now, with and without outputs pasted); `python tests/live_proof.py repro-first` ends proven (if unknown-skill, the FLEET wire is missing: rule FAIL naming exactly that gap, nothing else); lint or distill check exit 0 (10 or more pairs, body at most 2000 tokens, ASCII); grade 12 runs with/without plus lift; `node sprint/check.mjs` PASS.

Always: (a) full pytest equal or better than before (pre-existing out-of-scope fails named, not charged); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Built result, cut:
<task_result> RESULT: DONE - new skill repro-first built for the task Tool execution aborted class (12 pairs, live 6, distill ok, grade 1.0/0.0 lift 1.0) | proof: python tools/skill_trial.py grade --skill repro-first -> runs 12, with_rate 1.0, without_rate 0.0, lift 1.0 RESULT PASS </task_result>

Keeper facts: run builder-cure-reprofirst (seat builder, @builder), cure repro-first gate.
