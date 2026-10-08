---
role: judge
title: review read-abort v0.3.0 cure (DR-1007-13)
chain: review
of: 318-cure-100713
writer: builder
attempt: 1
origin_title: cure read-abort class v0.3.0 bump (DR-1007-13)
---
Review 318-cure-100713, built by builder. Its record: C:\empire\skillworks\sprint\queue\done\318-cure-100713.md (if missing, judge the tree and say so). Rerun its proof yourself, read its diff, check DR-1007-13's done-when as written (12 trial runs with beat 12 without by 0.3; suite equal or better; partly is FAIL). You never edit.

Run the skill checks and paste each result line: `python tests/live_proof.py read-abort-guard` ends proven; lint or distill check exit 0 (12 rules, body at most 2000 tokens, ASCII); grade 12 runs with/without plus lift; red replay one bad case fails before and passes now with outputs pasted; the bump is additive over v0.2.0 f4906a1, not a revert; `node sprint/check.mjs` PASS.

Always: (a) full pytest equal or better than before (pre-existing 6 named, not charged); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only skills/read-abort-guard/ plus queue records changed; no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
