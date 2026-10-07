---
role: builder
title: finish agentlint reseal plus adopt (O-007)
chain: start
attempt: 1
---
Goal: close O-007. builder-fix-agentlint resealed bash-allowlist (17 runs) plus bash-spawn-guard (12 runs) and adopted both to center master, leaving 1 warn from ready-file-check drift. ready-file-check v1.1.0 has now landed (5ce0e5c judge PASS). Reseal its trial-proof by rerunning the real grade suite (no hand edits), adopt the new fingerprint to center master exactly the way the prior packet did, and prove agentlint clean.

Scope: skills/ready-file-check/references/trial-proof.json (regen only) plus the center-master adopt step. Own paths only, never commit.

Proof: `python tools/skill_trial.py grade --skill ready-file-check` still 1.0/0.0 lift 1.0; `node C:/Users/me/Desktop/center/agentlint.mjs skillworks` prints 0 fail 0 warn; node sprint/check.mjs PASS.

Stop: m 20 min. Claim: append `O-007 | builder-fix-agentlint-finish | <UTC> | skills/ready-file-check/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. End with the RESULT line.
