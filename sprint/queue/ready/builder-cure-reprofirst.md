---
role: builder
title: cure repro-first gate (S50 trial)
chain: start
attempt: 1
---
Goal: serve DR-1007-5 (S50 trial 3 of 5: repro-first gate from the S49 cards). Check the board row DR-1007-5 for the class, trial proxy plus P2P. Build or bump the skill that carries this prompt upgrade; keep every existing pair green.

Scope: the row's trials sheet under evals/, the owning skill under skills/ or a new skill, its test. Own paths only, never commit. Check archive plus git history for repeats before building.

Proof: red replay first (one live case of the class, fails before, passes after); live_proof ends proven; lint or distill check exit 0 with 10 or more pairs; grade 12 runs with beats without by 0.3; python -m pytest tests/ -q and node sprint/check.mjs equal or better than before; nesting guard; no other repo's text or numbers.

Stop: M 45 min. Claim: append `DR-1007-5 | builder-cure-reprofirst | <UTC> | skills/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. Write `sprint/queue/done/builder-cure-reprofirst.md` with the RESULT plus proof lines before replying (no record, no review). End with the RESULT line.
