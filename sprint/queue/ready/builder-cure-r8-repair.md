---
role: builder
title: repair allowlist bump (a fleet failure to a proven skill) #8
chain: repair
of: builder-cure-r8
writer: builder
attempt: 2
origin_title: cure smith (a fleet failure to a proven skill) #8
---
The judge failed builder-cure-r8. Its verdict, cut:
<task_result> VERDICT: FAIL — allowlist bump proves green but row done-when unmet and tree out of scope. Changed: skills/bash-allowlist v1.0.0->v1.1.0, pairs 17 counted, trials 12 ids now ba-b07..b12+ba-g01..g06 (ba-b01..b06 replaced, QA edited). Reran: live_proof proven 6 passed; lint RESULT PASS 17 rules 725 tok; grade 12 runs 1.0/0.0 lift 1.0 PASS; test 3 passed; pytest 606 green; check 20/0/0 PASS. Done-when DR-1006-6 F2P needs class halve in 48h in loading repos + lift 0.3: no 48h adoption evidence, row still READY — partly is FAIL. Scope FAIL: 54 files dirty incl concurrent packets — judge skill files only per lead scoping (concurrent dirt is not this packet). Real thing: 5 new pair ids exist but trials were swapped not added; record builder-cure-r8.md missing so red unauditable. </task_result>

Lead scoping (binding): (a) F2P class-halving needs adoption plus 48 h re-scan per the row itself — judge the trial proxy (12 runs with beat 12 without by 0.3), not the 48 h clock; (b) concurrent dirty files are out of scope — judge only skills/bash-allowlist/, evals/bash-allowlist_trials.jsonl, tests/test_bash_allowlist.py.

Goal: fix exactly what the verdict names in-scope. Scope: skills/bash-allowlist/, evals/bash-allowlist_trials.jsonl, tests/test_bash_allowlist.py. Proof: the original proof plus (1) trials ADD the 5 new bad cases alongside ba-b01..b06 (restore replaced ids, no QA narrowing), (2) pasted bare-vs-bounded outputs for 3 of the 5 new pairs (red failed-before, green now). Stop: M 30 min; one repair only. End with the RESULT line.

Keeper facts: run 037-cure-allowlist-review (@judge), review allowlist bump #8.
VERDICT: FAIL
Changed: skills/bash-allowlist v1.0.0->v1.1.0, trials swapped not added, red unauditable.
