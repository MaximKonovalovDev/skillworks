---
role: judge
title: review multimatch cure (judge the tree)
chain: review
of: builder-cure-multimatch
writer: builder
attempt: 1
origin_title: cure multimatch misses (a fleet failure to a proven skill)
---
Review builder-cure-multimatch, built by builder. No done record was written, so judge the worktree diff directly against DR-1007-2's done-when (trial proxy: 12 runs with beat 12 without by 0.3; suite equal or better). You never edit. Scope: the multimatch skill (edit-unique v1.1.0 per the result, verify in tree), evals/edit-multimatch-1007_trials.jsonl, its test plus runner; concurrent dirt out of scope.

Rerun the proofs yourself and paste each result line: red replay (one multiple-matches case fails before, passes now, with and without outputs pasted); `python tests/live_proof.py <skill>` ends proven; lint or distill check exit 0 (10 or more pairs, body at most 2000 tokens); `python tools/skill_trial.py grade` 12 runs with/without plus lift; `node sprint/check.mjs` PASS.

Always: (a) full pytest equal or better than before (pre-existing out-of-scope fails named, not charged); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Built result, cut:
<task_result> RESULT: DONE - edit-unique bumped to v1.1.0 (SKILL.md:3-4 trigger names exact error + refuse/retry-once guard, SKILL.md:12 intro guard; live-proof.json + trial-proof.json resealed; scout sheet graded 12 runs 1.0/0.0 lift 1.0; 6 full-suite fails are other lanes' pre-existing dirt, none in scope; uncommitted) | proof: python skills/edit-unique/scripts/run_unique.py -> 12 of 12 pairs behave as written; grade 12 runs 1.0/0.0 lift 1.0; live_proof proven 6 passed; check.mjs 20/0/0 </task_result>

Keeper facts: run builder-cure-multimatch (seat builder, @builder), cure multimatch misses. No done record; judging the tree.
