---
role: judge
title: review fetch-github-first v0.2.0 cure (DR-1007-17)
chain: review
of: 348-cure-100717
writer: builder
attempt: 1
origin_title: cure webfetch 403/404 class bump (DR-1007-17)
---
Review 348-cure-100717, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\348-cure-100717.md (if missing, judge the tree and say so). Rerun its proof yourself, read its diff, check DR-1007-17's done-when as written (12 trial runs with beat 12 without by 0.3; suite equal or better; partly is FAIL). You never edit.

Run the skill checks and paste each result line: `python tests/live_proof.py fetch-github-first` ends proven; lint or distill check exit 0 (13 rules, body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs, no scaffold text, ASCII); red replay one bad case fails before and passes now with outputs pasted; grade 12 runs with/without plus lift; the bump is additive over v1.0.0 2f6f3c0, not a revert; `node sprint/check.mjs` PASS.

Always: (a) full pytest equal or better than the standing 6 (bash-spawn-guard pairs_md, c02 golden, engine-builder source, 2 stale live-proofs, seat untracked-state); name every FAILED line and charge any new one that traces to this diff; (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only skills/fetch-github-first/ plus queue records changed; no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
