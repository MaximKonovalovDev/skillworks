---
role: judge
title: review octokit FLEET wire fix (O-023)
chain: review
of: 336-wire-octokit
writer: builder
attempt: 1
origin_title: wire octokit-request into FLEET (O-023)
---
Review 336-wire-octokit, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\336-wire-octokit.md (if missing, judge the tree and say so). BK-1007-3 DONE 2a39744 landed the skill without a wire; this adds wire only. You never edit.

Rerun and paste each result line: `python tests/live_proof.py octokit-request` ends proven (was unknown skill); `python tools/install_fleet_skills.py --to C:/Users/me/.config/opencode/skills --check octokit-request` exit 0; `node sprint/check.mjs` PASS.

Always: (a) full pytest equal or better than the standing 6; name every FAILED line and charge any new one that traces to this diff; (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only gates.py plus installer plus new QA plus queue records changed, no SKILL edits; (e) ONE REAL THING: live_proof flips unknown-skill to proven on this diff, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
