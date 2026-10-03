---
role: judge
title: review K-17 skill_preview tool
---

Goal: Judge builder K-17 (skill_preview with README-then-SKILL.md fallback + PREVIEW_INPUT_SCHEMA + _validate_preview_args + list/call dispatch wiring + 1 test in tests/test_mcp_schema.py) for commit. Serves R3.
Scope: mcp_server/server.py (preview hunks only) + tests/test_mcp_schema.py (1 new test only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 28 passed); live stdio: tools/list shows both tools; skill_preview progit-branching returns SKILL.md head; missing skill -> is_error unknown-skill envelope; skill_search behavior unchanged.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-17 [S01-C3] | skill_preview + test, pytest 28 passed
Result: K-17 RESULT DONE 2026-10-03
