---
role: judge
title: verdict on read-offset-guard v1.4.0 bump
chain: review
of: builder-cure
writer: builder
attempt: 1
origin_title: cure offset bump for DR-1006-5
---
Review builder-cure, built by builder. Its record: C:\empire\skillworks\sprint\queue\claims.txt line `DR-1006-5 | builder-cure` (no done file; judge the tree and say so). Rerun its proof yourself, read its diff, check DR-1006-5's done-when as written (12 trial runs with beat 12 without by 0.3; suite equal or better; partly is FAIL). You never edit.

Run the skill checks and paste each result line: `python tests/live_proof.py read-offset-guard` ends proven; `python tools/skill_lint.py check --skill skills/read-offset-guard` exit 0 (builder: 21 rules 920 tok, 33 pairs); red replay one bad case fails before and passes now with outputs pasted; `python tools/skill_trial.py grade --skill read-offset-guard` runs with/without plus lift (builder: 13 runs 0.9231/0.0 lift 0.9231); `node sprint/check.mjs` PASS. FLEET wire must be present (builder: already wired, untouched) or FAIL naming exactly that gap.

Always: (a) full pytest equal or better than the standing baseline (builder reports 1391 passed 37 pre-existing out-of-scope FAILs none tracing to skill; name every FAILED line you see and charge any new one that traces to this diff); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed (skills/read-offset-guard/, evals sheet, tests/test_read_offset_guard.py, team/p3.md); no weakened gate, no edited QA, no deleted passing pair; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Halving note: class persists 20/48h per fresh scan; halving needs adoption plus 48 h and cannot pass same-day. Name whether you PASS on shape (pending adoption) or FAIL on the unmet halving; partly is FAIL.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
