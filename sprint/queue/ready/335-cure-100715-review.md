---
role: judge
title: review edit-unique v1.2.0 cure (DR-1007-15)
chain: review
of: 334-cure-100715
writer: builder
attempt: 1
origin_title: cure edit multi-match class bump (DR-1007-15)
---
Review 334-cure-100715, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\334-cure-100715.md (if missing, judge the tree and say so). Rerun its proof yourself, read its diff, check DR-1007-15's done-when as written (12 trial runs with beat 12 without by 0.3; suite equal or better; partly is FAIL). You never edit.

Run the skill checks and paste each result line: `python tests/live_proof.py edit-unique` ends proven; lint or distill check exit 0 (12 rules, body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs, no scaffold text, ASCII); red replay one bad case fails before and passes now with outputs pasted; grade 12 runs with/without plus lift; the bump is additive over v1.1.0 7bc042b, not a revert; `node sprint/check.mjs` PASS.

Always: (a) full pytest equal or better than the standing 6 (bash-spawn-guard pairs_md, c02 golden, engine-builder source, 2 stale live-proofs, seat untracked-state); name every FAILED line and charge any new one that traces to this diff; (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only skills/edit-unique/ plus queue records changed; no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
