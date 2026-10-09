---
role: judge
title: verdict on bash-allowlist v1.2.0 bump
chain: review
of: builder-cure
writer: builder
attempt: 1
origin_title: cure allowlist bump for DR-1006-6
---
Review builder-cure, built by builder. Its record: C:\empire\skillworks\sprint\queue\claims.txt line `DR-1006-6 | builder-cure | 2026-10-09T05:08Z` (no done file; judge the tree and say so). Rerun its proof yourself, read its diff, check DR-1006-6's done-when as written (12 trial runs with beat 12 without by 0.3; suite equal or better; partly is FAIL). You never edit.

Run the skill checks and paste each result line: `python tests/live_proof.py bash-allowlist` ends proven; lint `python tools/skill_lint.py check --skill skills/bash-allowlist` exit 0 (22 rules, body at most 2000 tokens, every rule has a locator that exists, 10 or more pairs, no scaffold text, ASCII); red replay one bad case fails before and passes now with outputs pasted; grade runs with/without plus lift (builder: 22 runs 1.0/0.0 lift 1.0); `node sprint/check.mjs` PASS. FLEET wire must be present (gates.py plus installer plus QA; v1.1.0 landed 5b484b5) or FAIL naming exactly that gap.

Always: (a) full pytest equal or better than the standing baseline (name every FAILED line; builder reports 1053 passed 29 failed all out-of-scope: export-guard, c02, stale proofs, dirty files; charge any new one that traces to this diff); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed (skills/bash-allowlist/, evals/bash-allowlist_trials.jsonl, tests/test_bash_allowlist.py, team/p3.md); no weakened gate, no edited QA; (e) ONE REAL THING: lift 0.3 or more on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
