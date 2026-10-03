---
role: judge
title: review K-29 MCP inputSchema + CacheHint + validation (server.py)
---

Goal: Judge builder K-29 (inspect-derived INPUT_SCHEMA query/skill/limit + _meta.cacheHint 1h + _validate_args is_error envelope + tests/test_mcp_schema.py 3 tests) for commit. Serves R3. NOTE: server.py now also holds 015 skills-dir work on top — judge K-29's scope only, flag any 015 bleed.
Scope: mcp_server/server.py (INPUT_SCHEMA derivation, cacheHint, _validate_args, _error_envelope, _search skill=None default) + tests/test_mcp_schema.py (new file only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 19 passed); live stdio session: tools/list shows inputSchema query/skill/limit + cacheHint; good call returns hits; limit 999 + missing query return is_error envelopes.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-29 [P2-SCHEMA-1001] | inputSchema + CacheHint + validation, pytest 19 passed
Result: K-29 RESULT DONE 2026-10-03
