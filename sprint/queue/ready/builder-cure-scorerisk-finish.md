---
role: builder
title: finish judge-score-risk wire plus re-proof
chain: start
attempt: 1
---
Goal: close DR-1007-4. The build is judged sound (lint 12 rules, grade 1.0/0.0 lift 1.0, red replay now documented) but the judge ruled FAIL wire-only: `python tests/live_proof.py judge-score-risk` exits 2 unknown skill, and seat-guard names its untracked tree. Read the ripgrep finish record (C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-book-ripgrep-finish.md) and mirror its wiring exactly: FLEET_SKILLS line in book2skill/gates.py, FLEET name in tools/install_fleet_skills.py, licence credit in THIRD_PARTY_NOTICES.md, tried line in team/p3.md. Do not rebuild the skill.

Scope: the 4 wire lines plus resealed proof files only. skills/judge-score-risk/ bodies stay untouched unless live_proof demands it. Own paths only, never commit.

Proof: `python tests/live_proof.py judge-score-risk` ends proven; grade rerun still with_rate 0.8 or more and lift 0.3 or more; `node sprint/check.mjs` PASS; no other repo's text or numbers.

Stop: m 20 min. Claim: append `DR-1007-4 | builder-cure-scorerisk-finish | <UTC> | FLEET wiring` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. Write `sprint/queue/done/builder-cure-scorerisk-finish.md` with the RESULT plus proof lines before replying (no record, no review). End with the RESULT line.
