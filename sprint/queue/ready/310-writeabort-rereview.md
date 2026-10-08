---
role: judge
title: re-review write-abort repair with FLEET wire (DR-1007-12)
chain: review
of: 303-cure-writeabort-repair
writer: builder
attempt: 1
origin_title: repair cure write-abort class (DR-1007-12)
---
Review 303-cure-writeabort-repair, built by builder. Its record: C:\empire\skillworks\sprint\queue\done\303-cure-writeabort-repair.md (if missing, judge the tree and say so). Rerun its proof yourself, read its diff, check DR-1007-12's done-when as written (12 trial runs with beat 12 without by 0.3; suite equal or better). You never edit.

Prior FAIL causes that must be gone: `python tests/live_proof.py write-abort-guard` ended `unknown skill` (missing FLEET wire in book2skill/gates.py plus installer list); stray root chunk.txt plus pycache; empty claim. Verify each is fixed or FAIL it again naming which remains.

Rerun and paste each result line: live_proof ends proven; lint or distill check exit 0 (12 rules, 24 pairs, body at most 2000 tokens, ASCII); grade 12 runs with/without plus lift; red replay one bad case fails before and passes now with outputs pasted; `node sprint/check.mjs` PASS.

Always: (a) full pytest equal or better than before (pre-existing out-of-scope fails named, not charged); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
