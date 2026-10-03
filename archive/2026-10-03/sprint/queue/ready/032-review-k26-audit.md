---
role: judge
title: review K-26 audit skips export output
---

Goal: Judge builder K-26 (audit.py skips any .md whose skill-relative path contains an `export` part, mirroring export.py:_own_output_ignore + test_audit_skips_export_dupes with %TEMP% fixture) for commit. Serves R1.
Scope: book2skill/audit.py (walk skip only) + tests/test_pipeline.py (one new test only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 23 passed); temp copy of skills/progit-branching audits N files/M tokens, unchanged after adding export-like dupes; confirm canonical counts exclude export parts and no other walk behavior changed.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-26 [AUDIT-SKIP-EXPORT-1001] | audit skips export/, counts canonical, pytest 23 passed
Result: K-26 RESULT DONE 2026-10-03
