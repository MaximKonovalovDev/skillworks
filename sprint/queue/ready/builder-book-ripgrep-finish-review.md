---
role: judge
title: review ripgrep-search build plus wire
chain: review
of: builder-book-ripgrep-finish
writer: builder
attempt: 1
origin_title: build ripgrep-search skill (book slice to proven skill)
---
Review builder-book-ripgrep-finish (plus its base builder-book-ripgrep), built by builder. Records: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-book-ripgrep-finish.md and C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-book-ripgrep.md. Rerun the proofs yourself, read the diff, check BK-1007-1's done-when as written (grade with_rate 0.8 or more and lift 0.3 or more over bare baseline; pytest green; check PASS). You never edit.

Run the check that fits what it made, and paste the result line of each:
1. A skill: `python tests/live_proof.py ripgrep-search` ends `proven`; distill or lint check exit 0 (body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs, no scaffold text, ASCII); grade rerun with/without numbers pasted.
2. Licence: every source line matches references/sources.md (Unlicense plus MIT only, no NonCommercial, no price).

Always: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before (out-of-scope concurrent failures named, not charged); (b) the nesting guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path in the diff passes 240 characters; (c) privacy: no other repo's path, text or number, no secret; sources stayed in work/ ignored; (d) only owned files changed (skills/ripgrep-search/, evals sheet, its test, FLEET wiring line, credit line); no weakened gate, no edited QA; (e) ONE REAL THING: grade lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Built result, cut:
<task_result> RESULT: DONE - wired ripgrep-search into the fleet: FLEET_SKILLS line book2skill/gates.py:71, FLEET name tools/install_fleet_skills.py:24, BurntSushi/ripgrep Unlicense-OR-MIT credit THIRD_PARTY_NOTICES.md:71, tried line team/p3.md:53, claim sprint/queue/claims.txt:2; skill bodies untouched | proof: live_proof ripgrep-search proven 11 passed; grade 12 runs 1.0/0.25 lift 0.75 PASS; check.mjs 20/0/0 </task_result>

Keeper facts: run builder-book-ripgrep-finish (seat builder, @builder), finish ripgrep-search wire plus re-proof.
