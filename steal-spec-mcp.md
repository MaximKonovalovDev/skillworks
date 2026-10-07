# Steal spec: MCP servers + sec gate (mcp-forge, folded into skillworks)

For inbox EB-2026-10-07-S66 (HUNT-MCP-2026). Donor card: center `research/cards/2026-10-07-mcp-forge-donors.md`. MIT + Apache-2.0, adapt with attribution.

## Exact takes

1. python-sdk v2 @91941ed: `src/mcp/server/apps.py:91` `def tool`, `:123` `ToolBinding`, `:88` cached list; `src/mcp/server/mcpserver/server.py:119-125` `warn_on_duplicate_*`, `:175-177/:200-204` wiring. Take: one binding type, loud duplicate warning, never silent overwrite.
2. agent-scan @2d3ca36: `src/agent_scan/direct_scanner.py:10` `is_direct_scan` + `:28` package-to-server-config; `src/agent_scan/guard.py:155` `run_guard`; `src/agent_scan/run.py:8` entry. Take: pre-run gate for every third-party server admitted.
3. registry (7321 stars): publish/discover metadata shape. Never the reference-servers set.
4. inspector (11031 stars): manual click-through conformance rig before any interop claim.
5. A2A (26033 stars): AgentCard advertisement envelope for fleet talk. Code read deferred.

Avoid: v1 `FastMCP` import paths (dead stub, raises); registry/inspector as runtime deps (directory + test rig, not libraries).

## Server template plan

`packs/server-template/`: 3 tools (ping, add, echo) on the ToolBinding shape + duplicate-knob guard. Scan gate: agent-scan runs against the verb list, report names each verb pass/flag.

## Scan-gate test

Done when: template selftest PASS + scan report covers the verb list with log attached, or REJECTED with reason.
