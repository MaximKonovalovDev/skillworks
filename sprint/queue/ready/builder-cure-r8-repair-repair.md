---
role: builder
title: repair repair allowlist bump (a fleet failure to a proven skill) #8
chain: repair
of: builder-cure-r8-repair
writer: builder
attempt: 2
origin_title: repair allowlist bump (a fleet failure to a proven skill) #8
---
The judge failed builder-cure-r8-repair. Its verdict, cut:
<task id="ses_eea63b32fffeo6s2bfP9J6JM2n" state="completed"> <task_result> VERDICT: FAIL Changed (in-scope): skills/bash-allowlist v1.1.0->v1.2.0, trials 22 ids ba-b01..b06 restored ADD-only +5 new v1.2.0 shapes; packet claimed 17 tasks +5 lines, tree now 85 ins 22 tasks. Trial proxy PASS but P2P fails: grade 22 runs 1.0/0.0 lift 1.0 PASS (was 17 1.0/0.0); lint 22 rules 910 tok PASS (was 17/725); live_proof bash-allowlist proven 6 passed; test_bash_allowlist 3 passed 3 skipped; check 20/0/0 PASS. Full pytest 721 passed 2 failed c02-golden + seat_guard-untracked (was 605 passed 1 FAIL) — not equal/better, P2P pytest green unmet. Nest guard empty PASS, paths max 49<240 PASS, privacy no hit PASS. One real thing: trials ADD holds (22 ids include ba-b01..b06), grade lift 1.0 moves, but packet's 17-task red-green record path done/... missing (file in running/ + work red-green.txt git-ignored) unverifiable as written. Revert: `git checkout HEAD -- skills/bash-allowlist evals/bash-allowlist_trials.jsonl tests/test_bash_allowlist.py` </task_result> </task>

Goal: fix exactly what the verdict names. Scope: the files of the original packet (C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-r8-repair-review.md). Proof: the original proof plus the verdict's failing check. Stop: M 30 min; one repair only. End with the RESULT line.

Keeper facts: run builder-cure-r8-repair-review (@judge), review allowlist repair (a fleet failure to a proven skill) #8.
VERDICT: FAIL
Changed (in-scope): skills/bash-allowlist v1.1.0->v1.2.0, trials 22 ids ba-b01..b06 restored ADD-only +5 new v1.2.0 shapes; packet claimed 17 tasks +5 lines, tree now 85 ins 22 tasks.
