---
role: builder
title: cure webfetch timeout misses (a fleet failure to a proven skill)
chain: start
attempt: 1
---
Goal: serve DR-1007-3. Tame webfetch Request timed out misses (12 in 48 h): retry with backoff plus timeout naming instead of a bare re-fetch. Check the board row DR-1007-3 for the trial proxy plus P2P; note DR-1006-7 websearch-retry is DONE and distinct (backend-busy plus missing-key), prefer a version bump of the skill that owns timeouts if one exists, else a new skill.

Scope: evals/webfetch-retry_trials.jsonl (12 scout tasks on disk, extend to a graded sheet), the owning skill under skills/ or a new skill, its test. Own paths only, never commit. Check archive plus git history for repeats before building.

Proof: red replay first (one live timeout miss, fails before, passes after); live_proof ends proven; lint or distill check exit 0 with 10 or more pairs; grade 12 runs with beats without by 0.3; python -m pytest tests/ -q and node sprint/check.mjs equal or better than before; nesting guard; no other repo's text or numbers.

Stop: M 45 min. Claim: append `DR-1007-3 | builder-cure-webfetch | <UTC> | skills/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. Write `sprint/queue/done/builder-cure-webfetch.md` with the RESULT plus proof lines before replying (no record, no review). End with the RESULT line.
