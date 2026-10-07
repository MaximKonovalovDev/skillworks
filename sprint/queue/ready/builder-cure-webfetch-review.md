---
role: judge
title: review webfetch-retry cure
chain: review
of: builder-cure-webfetch
writer: builder
attempt: 1
origin_title: cure webfetch timeout misses (a fleet failure to a proven skill)
---
Review builder-cure-webfetch, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-webfetch.md (if missing, judge the tree and say so). Rerun the proofs yourself, read the diff, check DR-1007-3's done-when as written (trial proxy: 12 runs with beat 12 without by 0.3; suite equal or better). You never edit. Scope: the webfetch skill (new webfetch-retry per the result, verify in tree; must be distinct from DONE websearch-retry DR-1006-7), evals/webfetch-retry_trials.jsonl, its test; concurrent dirt out of scope.

Rerun and paste each result line: red replay (one timeout case fails before, passes now, with and without outputs pasted); `python tests/live_proof.py <skill>` ends proven; lint or distill check exit 0 (10 or more pairs, body at most 2000 tokens, ASCII); grade 12 runs with/without plus lift; `node sprint/check.mjs` PASS.

Always: (a) full pytest equal or better than before (pre-existing out-of-scope fails named, not charged); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Built result, cut:
<task_result> RESULT: DONE - new skill webfetch-retry (12 pairs, live 6/6, grade lift 1.0, distill ok, audit clean) | proof: python tools/skill_trial.py grade --skill webfetch-retry -> runs 12, with_rate 1.0, without_rate 0.0, lift 1.0, RESULT PASS </task_result>

Keeper facts: run builder-cure-webfetch (seat builder, @builder), cure webfetch timeout misses.
