---
role: judge
title: review hyperfine-bench skill build (BK-1007-13)
chain: review
of: 351-book-hyperfine
writer: builder
attempt: 1
origin_title: build hyperfine-bench skill from scouted slice (BK-1007-13)
---
Review 351-book-hyperfine, built by builder. Its record: C:\empire\skillworks\sprint\queue\done\351-book-hyperfine.md (if missing, judge the tree and say so). Rerun its proof yourself, read its diff, check BK-1007-13's done-when as written (grade with_rate 0.8 or more lift 0.3 or more; suite equal or better; partly is FAIL). You never edit.

Run the skill checks and paste each result line: `python tests/live_proof.py hyperfine-bench` ends proven; lint or distill check exit 0 (12 rules, body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs, no scaffold text, ASCII); red replay one bad case fails before and passes now with outputs pasted; grade 12 runs with/without plus lift; `node sprint/check.mjs` PASS. FLEET wire must be present (gates.py plus installer plus 10-row QA, lesson of DR-1007-12) or FAIL naming exactly that gap.

Always: (a) full pytest equal or better than the standing 1 fail (c02 golden top git-one-branch vs progit-branching); name every FAILED line and charge any new one that traces to this diff; (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
