---
role: judge
title: review K-34/K-35 EPUB body-only + pagebreak map
---

Goal: Judge builder K-34/K-35 (extract.py _read_epub body-subtree select + nav/script/style + epub nav/toc removal + pagebreak id/label map with heading fallback + EPUB pages list in receipt + 2 fixture tests, no binaries) for commit. Serves R1/R4.
Scope: book2skill/extract.py (EPUB lane only) + tests/test_pipeline.py (2 new tests only). Ideas-only AGPL reimplementation — verify no verbatim ebooklib paste.
Proof: rerun `python -m pytest tests/ -q` yourself (expect 26 passed); nav-heavy EPUB head/nav-free + pages [] and pagebreak fixture [{p1,7},{p2,Eight},{p3,Chapter One}]; PDF pages int count untouched.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-34/K-35 [S16-C1/C2] | body-only + pagebreak map, ideas-only, pytest 26 passed
Result: K-34/K-35 RESULT DONE 2026-10-03
