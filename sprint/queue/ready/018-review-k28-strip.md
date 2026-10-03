---
role: judge
title: review K-28 Gutenberg marker strip (extract.py + test)
---

Goal: Judge builder K-28 (strip_gutenberg_markers() in book2skill/extract.py + test_gutenberg_marker_strip, freud re-extract 1241682->1222093 chars header/footer gone) for commit. Serves R4.
Scope: book2skill/extract.py (strip function + stripped receipt + default-on flag) + tests/test_pipeline.py (one new test only). Reimplemented MIT idea (kiasar/gutenberg_cleaner, ideas-only, no paste) — verify no verbatim copy; THIRD_PARTY_NOTICES.md attribution line still missing (note as follow-up, do not FAIL for it alone).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 17 passed); re-run extract on work/freud-dreams and confirm header/footer gone + receipt stripped:true; confirm opt-out flag works.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-28 [P3-STRIP-1001] | marker strip + test, freud header/footer gone, pytest 17 passed
Result: K-28 RESULT DONE 2026-10-03
