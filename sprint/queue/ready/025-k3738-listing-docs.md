---
role: builder
title: K-37/K-38 listing shape + files block (PREP-ONLY docs only)
chain: start
---

Goal: K-37 + K-38 DONE (R6): listing.md gains status/category/tags/files shape (+6 docs lines) + Vol 0 line carries filename+size+date (+2 docs lines). PREP-ONLY, no paid ship, no ToS paste, no fee numbers as fact (K-27 gates all paid implications).
Scope: skills/progit-branching/listing.md ONLY (docs lines). No code, no other files.
Proof: listing.md has status + category + tags + files block AND Vol 0 line with filename+size+date + `node sprint/check.mjs` PASS (exit 0) + `python -m pytest tests/ -q` green (expect 20 passed, no new test needed — docs only).
Stop: S 20 min. End with the RESULT line.
Record: K-37/K-38 [S19-C2/C4] | listing shape + files block, PREP-ONLY, check PASS
Board: sprint/board.md K-37 + K-38 READY -> DONE need judge PASS + commit by lead.
