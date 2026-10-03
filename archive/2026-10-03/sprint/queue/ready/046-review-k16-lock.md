---
role: judge
title: review K-16 export lock receipt
---

Goal: Judge builder K-16 (export.py skill_version() from frontmatter default 0.1.0 + dest/.lock.json {name, version, eval-rate, target, date} per target + tests/test_export_lock.py) for commit. Serves R5.
Scope: book2skill/export.py (version+lock only) + tests/test_export_lock.py (new only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 30 passed); lock carries exactly the 5 keys with correct values; version-less frontmatter defaults 0.1.0; gate/ignore logic untouched.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-16 [S01-C2] | lock receipt per target + test, pytest 30 passed
Result: K-16 RESULT DONE 2026-10-03
