---
role: judge
title: review gron-json skill build (BK-1007-8)
chain: review
of: 322-book-gronjson
writer: builder
attempt: 1
origin_title: build gron-json skill from scouted slice (BK-1007-8)
---
Review 322-book-gronjson, built by builder. Its record: C:\empire\skillworks\sprint\queue\done\322-book-gronjson.md (if missing, judge the tree and say so). Rerun its proof yourself, read its diff, check BK-1007-8's done-when as written (grade with_rate 0.8 or more lift 0.3 or more; suite equal or better; partly is FAIL). You never edit.

Run the skill checks and paste each result line: `python tests/live_proof.py gron-json` ends proven; lint or distill check exit 0 (12 rules, body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs, no scaffold text, ASCII); red replay one bad case fails before and passes now with outputs pasted; grade 12 runs with/without plus lift; `node sprint/check.mjs` PASS. FLEET wire must be present (gates.py plus installer plus 10-row QA, lesson of DR-1007-12) or FAIL naming exactly that gap.

Always: (a) full pytest equal or better than before (pre-existing 6 named, not charged); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed (skills/gron-json/, tests/test_gron_json.py, evals/gron-json files, FLEET wires, queue records); no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
