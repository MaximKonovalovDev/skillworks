---
role: judge
title: review bat-cat skill build (BK-1007-9)
chain: review
of: 325-book-batcat
writer: builder
attempt: 1
origin_title: build bat-cat skill from scouted slice (BK-1007-9)
---
Review 325-book-batcat, built by builder. Its record: C:\empire\skillworks\sprint\queue\done\325-book-batcat.md (if missing, judge the tree and say so). Rerun its proof yourself, read its diff, check BK-1007-9's done-when as written (grade with_rate 0.8 or more lift 0.3 or more; suite equal or better; partly is FAIL). You never edit.

Run the skill checks and paste each result line: `python tests/live_proof.py bat-cat` ends proven; lint or distill check exit 0 (12 rules, body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs, no scaffold text, ASCII); red replay one bad case fails before and passes now with outputs pasted; grade 12 runs with/without plus lift; `node sprint/check.mjs` PASS. FLEET wire must be present (gates.py plus installer plus 10-row QA) or FAIL naming exactly that gap.

Suite regression check (builder reports 8 fails vs the standing 6): list all 8 FAILED lines with names. The standing 6 are bash-spawn-guard pairs_md, c02 golden, engine-builder source, 2 stale live-proofs, seat untracked-state. If any fail outside those 6 traces to this diff (gates.py, installer, THIRD_PARTY, bat-cat files), the verdict is FAIL naming it, even when the skill gates are green.

Always: (a) equal or better than before, new regressions charged; (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed; no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
