---
role: builder
title: finish axios-get wire plus re-proof
chain: start
attempt: 1
---
Goal: close BK-1007-2. builder-book-axiosget built skills/axios-get/ (lint 799 tok, grade 1.0 lift 1.0) but the judge ruled FAIL wire-only: `python tests/live_proof.py axios-get` prints unknown skill. Read the ripgrep finish record (C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-book-ripgrep-finish.md) and mirror its wiring exactly: FLEET_SKILLS line in book2skill/gates.py, FLEET name in tools/install_fleet_skills.py, licence credit in THIRD_PARTY_NOTICES.md, tried line in team/p3.md. Do not rebuild the skill.

Scope: the 4 wire lines plus resealed proof files only. skills/axios-get/ bodies stay untouched unless live_proof demands it. Own paths only, never commit.

Proof: `python tests/live_proof.py axios-get` ends proven; grade rerun still with_rate 0.8 or more and lift 0.3 or more; `node sprint/check.mjs` PASS; Unlicense-or-MIT only, no other repo's text or numbers.

Stop: m 20 min. Claim: append `BK-1007-2 | builder-book-axiosget-finish | <UTC> | FLEET wiring` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. Write `sprint/queue/done/builder-book-axiosget-finish.md` with the RESULT plus proof lines before replying (no record, no review). End with the RESULT line.
