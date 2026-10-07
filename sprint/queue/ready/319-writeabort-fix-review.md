---
role: judge
title: review write-abort narrow fix (DR-1007-12)
chain: review
of: 317-writeabort-fix
writer: builder
attempt: 1
origin_title: narrow fix write-abort installer wire plus cleanup (DR-1007-12)
---
Review 317-writeabort-fix, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\317-writeabort-fix.md (if missing, judge the tree and say so). This closes the 310 second-FAIL gaps; skill content stands proven (grade 1.0/0.0 lift 1.0, lint 12/24/763, live 6). You never edit.

Rerun and paste each result line: `python tools/install_fleet_skills.py --to C:/Users/me/.config/opencode/skills --check write-abort-guard` exit 0; `python tests/live_proof.py write-abort-guard` ends proven; root chunk.txt gone plus no new pycache; claims.txt carries a DR-1007-12 line; `node sprint/check.mjs` PASS.

Always: (a) full pytest equal or better than before (pre-existing 6 named, not charged); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only installer plus deletions plus claim changed, no SKILL or QA edits; (e) ONE REAL THING: the installer check flips to exit 0 with the wire on this diff, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
