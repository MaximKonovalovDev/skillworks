# w2-steal: top 3 to steal/rewrite

Date: 2026-10-06. Loop OFF. Donors read live, all MIT.

## T1 — server template (from python-sdk)
Source: modelcontextprotocol/python-sdk `src/mcp/server/fastmcp/` + `examples/`. License: MIT (Anthropic 2024), read 2026-10-06.
What: FastMCP `@mcp.tool()`, lifespan, stdio/SSE transports.
Rewrite: `packs/server-template/` — one minimal Python server with one tool, one resource, one prompt.
Proof: `python packs/server-template/server.py --selftest`.

## T2 — sec gate (from mcp-go)
Source: mark3labs/mcp-go `server/server.go` (`ToolHandlerMiddleware`, `ToolFilterFunc`, `Hooks`). License: MIT, read 2026-10-06.
What: typed tools plus middleware chain and list/call filters.
Rewrite: `packs/sec-gate/` — allow-list filter + logging middleware + deny test.
Proof: `go test ./packs/sec-gate/`.

## T3 — gateway router (from mcp-use)
Source: mcp-use/mcp-use `libraries/` session + connectors. License: MIT (pietrozullo 2025), read 2026-10-06.
What: one agent session over N servers, config-based connect.
Rewrite: `packs/gw-router/` — config lists 2 servers, route call by name.
Proof: `node packs/gw-router/router.mjs --selftest`.

## Catalog method (from awesome-mcp-servers)
Source: punkpeye/awesome-mcp-servers `README.md`. License: MIT (Fiegel), read 2026-10-06.
Use: category list seeds our steal map; no code copied.

Order: T1, then T2, then T3. Each <200 net lines.
