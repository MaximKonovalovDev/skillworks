---
role: builder
title: reseal git-one-branch stale live proof (Vol1 upkeep)
chain: start
attempt: 1
---
Goal: Vol1 upkeep, mirroring the bevy reseal (a3b9832 judge PASS). `python -m pytest tests/ -q` names fleet git-one-branch live-proof match FAIL: fingerprint stale (proof 2026-10-06T18:07Z era, skill since changed by O-008-adjacent work or proof expiry). Make git-one-branch pass its own gates again.

Scope: skills/git-one-branch/ plus its live proof only. Own repo paths only, never commit. No other repo's text, paths or numbers in any committed file. skills/git-one-branch bodies stay untouched unless live_proof demands it; prefer reseal, fix only what the failing gate names.

Proof: fleet git-one-branch live-proof match green; `python tests/live_proof.py git-one-branch` ends proven fresh; eval rate at gate; `node sprint/check.mjs` PASS.

Stop: m 20 min. Claim: append `VOL1 | builder-gitonebranch-reseal | <UTC> | skills/git-one-branch/` to sprint/queue/claims.txt first, only if no claim on the path in the last 2 h. Write `sprint/queue/done/builder-gitonebranch-reseal.md` with the RESULT plus proof lines before replying (no record, no review). End with the RESULT line.
