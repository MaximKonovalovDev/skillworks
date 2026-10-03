---
name: mcp-server-tester
description: Use when changing mcp_server/server.py or its tools and you must prove handshake, search, preview, and bad calls still behave over stdio.
---

# MCP Server Tester

Test the `skill_search` server the way a client meets it: stdio
handshake, `tools/list`, `tools/call`, then the abuse cases. Protocol
first (JSON-RPC 2.0), unit details second.

## 1. Handshake and list

```powershell
python mcp_server/server.py
python -m pytest tests/test_mcp_schema.py tests/test_mcp_rank.py tests/test_mcp_skills_dir.py -q
```

Every new tool needs: `tools/list` shows it, `_input_schema` derives
from the handler signature, unknown names return the guided error.

## 2. Call matrix

- Good call: `_search` ranks the expected skill first with rank fields.
- Preview: `_preview` returns the head; unknown skill errors cleanly.
- Bad call: missing/invalid args rejected by `_validate_args`, error
  envelope shape unchanged.
- Out-of-tree skills dir via env override and flag both serve.

## 3. Compliance checklist

- JSON-RPC 2.0 message shapes; error codes standard, no tracebacks leak.
- Schemas (Pydantic-style dicts) enforced before the handler runs.
- No secrets in logs or errors; `skills/*/export/` never served.
- Coverage of the call matrix above stays green, not just unit helpers.

## 4. Regression

After any server edit, rerun the full suite (`python -m pytest tests/ -q`)
plus one live stdio session: handshake, list, call, bad call. Log the
one-line result; a bare agent report proves nothing.

## Do not

- Test helpers without the stdio path. Change the error envelope to
  make a test pass. Commit a skill dir that only passes in-tree.
Source: https://github.com/VoltAgent/awesome-claude-code-subagents (MIT, fetched 2026-10-03)
