---
role: judge
title: review K-20 single-flight refresh
---

Goal: Judge builder K-20 (refresh.py receipt.json on both paths, no-op returns changed:False + fingerprint, index.py untouched + tests/test_refresh_noop.py twice-run) for commit. Serves R1.
Scope: book2skill/refresh.py (guard+receipt only) + tests/test_refresh_noop.py (new only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 30 passed); first run changed True, second no-ops matching fingerprint, index bytes unchanged, receipt equals return.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-20 [S02-C4] | single-flight refresh + test, pytest 30 passed
Result: K-20 RESULT DONE 2026-10-03
