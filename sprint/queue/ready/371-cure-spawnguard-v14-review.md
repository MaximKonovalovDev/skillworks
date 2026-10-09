---
role: judge
title: verdict on bash-spawn-guard v1.4.0 repair
chain: review
of: builder-cure
writer: builder
attempt: 1
origin_title: cure spawn-guard bump for DR-1006-3
---
Review builder-cure, built by builder. Its record: C:\empire\skillworks\sprint\queue\claims.txt line `DR-1006-3 | builder-cure | 2026-10-09T08:14Z` (no done file; judge the tree and say so). This is a repair: auto-backup d5e7b47 rolled SKILL 1.4.0 back to 1.3.0 while pairs.json stayed at 32; the cure restored the 5 dispatch rules plus errors plus sources and re-proved, no new pairs, none deleted. Rerun its proof yourself, read its diff, check DR-1006-3's done-when as written (12 trial runs with beat 12 without by 0.3; suite equal or better; partly is FAIL). You never edit.

Run the skill checks and paste each result line: `python tests/live_proof.py bash-spawn-guard` ends proven (builder: 10 passed); `python tools/skill_lint.py check --skill skills/bash-spawn-guard` exit 0 (builder: 32 rules 1251 tok); red replay detached-check kill fails bare and receipt-poll passes bounded, outputs pasted; `python tools/skill_trial.py grade --skill bash-spawn-guard` runs with/without plus lift (builder: 12 runs 1.0/0.0 lift 1.0); `node sprint/check.mjs` PASS. FLEET wire must be present (landed v1.3.0 0af4040) or FAIL naming exactly that gap.

Always: (a) full pytest equal or better than the standing baseline (name every FAILED line you see; known standing fails: export-guard, c02, stale proofs, cli.py SyntaxError collectors; charge any new one that traces to this diff); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed (skills/bash-spawn-guard/, team/p3.md); confirm the restored rules match the pre-rollback v1.4.0 text rather than new invention; no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Halving note: class reads UP (330 to 933 per pilot1009); halving needs adoption plus 48 h and cannot pass same-day; clock lives on AD-1006-1. Name whether you PASS on shape or FAIL on unmet halving; partly is FAIL.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
