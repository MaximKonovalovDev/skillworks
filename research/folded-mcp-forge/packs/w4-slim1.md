# w4-slim1

Date: 2026-10-06. Loop OFF. Scope: `packs/w4-slim1.md` only. No code yet.

## Keep: 3 servers max

1. `packs/server-template/` (T1). One tool, one resource, one prompt.
2. `packs/sec-gate/` (T2). Allow-list filter plus log middleware.
3. One demo server. Small copy of T1 with a new tool. Proves reuse.

No fourth server until these three pass.

## Drop: gateway

Drop `packs/gw-router/` (T3) for now. It needs N servers live. Too big for W4. Back after T1 and T2 pass.

## Rules

One target at a time. Each under 200 net lines. Each with its own proof. Order: T1, then T2, then demo.

## Proof

`python packs/server-template/server.py --selftest`
`go test ./packs/sec-gate/`
`node sprint/check.mjs` in `C:/Users/me/Desktop/mcp-forge`
