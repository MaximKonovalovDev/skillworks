---
role: builder
title: K-34/K-35 EPUB body-only + pagebreak map in extract
chain: start
---

Goal: K-34 + K-35 DONE (R1/R4): reimplement ideas-only (AGPL, never paste) in book2skill/extract.py _read_epub — (a) body-subtree select (soup.body equivalent, drop head/nav chrome) + (b) pagebreak-label page map (epub:type pagebreak id/label fallback) + pages list in extract() receipt (empty when none).
Scope: book2skill/extract.py (EPUB lane only) + tests (fixtures + 2 tests: nav-heavy EPUB head/nav-free; pagebreak fixture pages list + empty-when-none). No other stages. Titled-chunk scan (S16-C3) folds into the pagebreak test, no separate lane.
Proof: nav-heavy EPUB full_text head/nav-free + receipt pages list on pagebreak fixture (empty when none) + `python -m pytest tests/ -q` green (expect 25 passed: 23 + 2 new).
Stop: M 40 min. End with the RESULT line.
Record: K-34/K-35 [S16-C1/C2] | body-only + pagebreak map, ideas-only, pytest 25 passed
Board: sprint/board.md K-34 + K-35 READY -> DONE need judge PASS + commit by lead.
