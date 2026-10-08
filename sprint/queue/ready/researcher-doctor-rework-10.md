---
role: researcher
title: webfetch timeout sheet rework with real cases
chain: rework
of: researcher-doctor-scout-10
attempt: 2
---
Goal: fix the FAIL on DR-1007-20. Judge found all 12 tasks in evals/webfetch-timeout-1007h_trials.jsonl use literal `<url>` and owner-name placeholders with run:null, and no real thing moved. Rewrite the sheet with REAL cases from the own fleet failure corpus (own MIT data): each of the 12 tasks names a real failing repo plus the real timed-out URL pattern plus the real error line from the scan window, and each task is runnable (pinned run command, no run:null, no placeholders).

Scope: rewrite evals/webfetch-timeout-1007h_trials.jsonl (same 12 ids wt8-b01 to wt8-b06 plus wt8-g01 to wt8-g06) plus update the DR-1007-20 board row evidence only. Own paths only, never commit. Privacy holds: own corpus data only, no external text, no secrets. Write `sprint/queue/done/researcher-doctor-rework-10.md` with the RESULT plus proof lines before replying.

Proof: `Select-String -Pattern '<url>|owner-name|run:null' evals/webfetch-timeout-1007h_trials.jsonl` returns nothing; `node sprint/check.mjs` PASS after the board edit; name one real thing the rework moved (a real case count, a tied number, a replayed failure).

Stop: M 30 min. Claim: append `REWORK | researcher-doctor-rework-10 | <UTC> | DR-1007-20` to sprint/queue/claims.txt first. End with the RESULT line.
