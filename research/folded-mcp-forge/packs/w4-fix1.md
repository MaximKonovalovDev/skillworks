# w4-fix1: server-template selftest

Date: 2026-10-06. Loop OFF. Scope: `packs/` only. Rewrite, no code copied.

## Fix

`packs/server-template/server.py` follows python-sdk FastMCP shape (donor: modelcontextprotocol/python-sdk, MIT, read 2026-10-06 per `packs/w2-steal.md`): `FastMCP("forge-template")` plus `@mcp.tool()`.

Three tools: `ping() -> pong`, `add(a:int, b:int)`, `echo(text:str)`. Allow-list `ALLOWED = {ping, add, echo}`.

Deny test: call unknown tool `rm_rf` via the tool manager. It must raise. Nothing runs.

## Selftest checks

1. `list_tools()` names exactly `add, echo, ping`.
2. Names equal `ALLOWED` (no drift).
3. `ping` returns non-empty.
4. Unknown tool raises (deny ok).

## Proof

`python packs/server-template/server.py --selftest` -> `SELFTEST PASS: tools=add,echo,ping deny=ok`.

`node sprint/check.mjs` -> packs pass; vision still FAILs on K-01 (Scorecard and steal map empty). Local proof only.

## Next

T2 sec-gate, then T3 router. Each under 200 lines.
