---
role: runner
title: Prune dead claim lines older than 2h in sprint/queue/claims.txt
---

Goal: Clear the center size FAIL (`sprint/queue/claims.txt`: 67 dead claim lines whose runs ended hours ago and the keeper never saw end) by deleting claim lines older than 2 h, keeping at most the 20 most recent lines.

Scope: `sprint/queue/claims.txt` only. No other file. Never `git add -A`; helpers never commit.

Proof: before/after line counts with `(Get-Content sprint/queue/claims.txt | Measure-Object -Line).Lines`, newest remaining timestamp within policy, and the size check the keeper named no longer FAILs.

Stop: S 15 min. DONE only with the counts pasted in the result plus `RESULT: DONE - <what> | proof: <where>`.
