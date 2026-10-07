---
role: builder
title: rebuild Fleet Vol 1 gate after trim plus proof churn (O-011)
chain: start
---
Goal: serve O-011 (R6 shop proof). `python tools/pack_check.py packs/fleet-vol-1` prints RESULT FAIL 3 findings on the current tree (lead recheck 2026-10-07T19:30Z: zip stale on proof/bevy-rust-ecs-live-proof.json plus proof/pwsh-for-bash-writers-live-proof.json plus proof/real-browser-automation-live-proof.json; factory preflight JUDGE FAIL missing). Rebuild the zip from the current tree and close the preflight gap so the gate prints RESULT PASS with 0 findings.

Scope: packs/fleet-vol-1/ (rebuild via python tools/pack_build.py, never hand-zip; dist/ is git-ignored, never committed) plus team/p5.md (one log line) plus the factory JUDGE preflight (attach or request the independent JUDGE.md PASS; if no judge PASS exists, report HOLD for re-judge, do not fake it). Own paths only, never commit. The tree is churning under a concurrent trim: rebuild the zip LAST, after every other proof run in this packet, then run pack_check twice.

Proof: `python tools/pack_check.py packs/fleet-vol-1` ends RESULT PASS with 0 findings (paste both runs); `node sprint/check.mjs` PASS; licences: no NonCommercial source priced (vol0 git-one-branch CC-BY-NC-SA-3.0 stays free). Write `sprint/queue/done/312-pack-rebuild2.md` with the RESULT plus proof lines before replying (no record, no review).

Stop: M 30 min. Claim: append `O-011 | 312-pack-rebuild2 | <UTC> | packs/fleet-vol-1/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. End with the RESULT line.

End your reply with one line: `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what changed, or the blocker> | proof: <command result, file or URL>`.
