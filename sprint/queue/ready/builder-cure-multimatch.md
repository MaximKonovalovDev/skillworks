---
role: builder
title: cure multimatch misses (a fleet failure to a proven skill)
chain: start
attempt: 1
---
Goal: serve DR-1007-2. Tame the edit Found multiple matches class (27 in 48 h, 7 repos, 0 loads): when oldString matches more than once, resolve or refuse with a named guard instead of a blind edit. Prefer a version bump of the skill that owns this class if one exists, else a new skill; keep every existing pair green.

Scope: evals/edit-multimatch-1007_trials.jsonl (12 scout tasks on disk, extend to a graded sheet), the owning skill under skills/ or a new skills/edit-multimatch/, its test. Own paths only, never commit. Check the board row DR-1007-2 for the trial proxy plus P2P.

Proof: red replay first (one live multiple-matches miss, fails before, passes after); live_proof ends proven; lint or distill check exit 0 with 10 or more pairs; grade 12 runs with beats without by 0.3; python -m pytest tests/ -q and node sprint/check.mjs equal or better than before; nesting guard; no other repo's text or numbers.

Stop: M 45 min. Claim: append `DR-1007-2 | builder-cure-multimatch | <UTC> | skills/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. End with the RESULT line.
