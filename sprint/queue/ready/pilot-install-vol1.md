---
role: pilot
title: log Vol1 loads run (S110)
chain: start
attempt: 1
---
Goal: serve PIPE-1007-1 (inbox S110: one Vol1 skill passes tests and logs 10 loads in 24 h across repos). Read packs/fleet-vol-1/pack.json first: Vol1 is pwsh-for-bash-writers plus real-browser-automation plus bevy-rust-ecs (vol0 git-one-branch is NC free, never sold, out of scope). Pick the strongest (pwsh unless scans say otherwise), install latest into repos that accept it, log the loads.

Scope: tools/install_fleet_skills.py runs, the loads scan, adopted.csv in C:/Users/me/.empire/state/skilldoctor/ (private state, never committed to this public repo). Own paths only, never commit. No other repo's text, paths or numbers in any committed file; report counts only.

Proof: loads scan output showing 10 or more loads in 24 h for the chosen Vol1 skill; installer receipts named; `node sprint/check.mjs` PASS.

Stop: M 30 min. Claim: append `PIPE-1007-1 | pilot-install-vol1 | <UTC> | installer` to sprint/queue/claims.txt first, only if no claim on the row in the last 2 h. End with the RESULT line.
