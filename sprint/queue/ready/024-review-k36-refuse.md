---
role: judge
title: review K-36 build refuses name/dir mismatch
---

Goal: Judge builder K-36 (build() refuses --name != dir basename or bad charset with rule quoted; CLI maps to UsageError exit 2; existing layout test fixed to matching pair + new test_build_refuses_name_dir_mismatch) for commit. Serves R1, closes 016.
Scope: book2skill/build.py + book2skill/cli.py (wiring only) + tests/test_pipeline.py (fixed test + 1 new test).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 20 passed); mismatch pair exit 2 with rule quoted + no traceback; matching pair exit 0; confirm refusal also fires on direct build() call (not just CLI) and charset rule enforced.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-36 [016] | name/dir refuse + test, pytest 20 passed
Result: K-36 RESULT DONE 2026-10-03
