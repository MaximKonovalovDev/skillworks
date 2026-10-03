---
role: judge
title: review 005-export-target (clean usage error)
---

Goal: Judge 005 (unknown --target gives clean usage error, no traceback) for commit.
Scope: book2skill/cli.py, book2skill/export.py, tests/test_pipeline.py (new unknown-target test only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 9 passed); run export with --target bogus (expect exit 2, two-line usage error naming the 4 legal targets, no Traceback). Verify traceback is gone on both CLI and direct-export paths.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: 005-pilot-export-target | Choice+UsageError, pytest 9 passed
Result: 005 RESULT DONE 2026-10-03
