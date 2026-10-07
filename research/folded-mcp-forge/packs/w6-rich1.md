# w6-rich1: Rich 3-tool server demo

Date: 2026-10-06. Loop OFF. Scope: `packs/w6-rich1.md` only. No code copied.

## User

Rich. First outside demo of `packs/server-template/server.py`. Three tools only: `ping`, `add`, `echo`.

## Demo

1. Run `python packs/server-template/server.py --selftest`. Want `SELFTEST PASS: tools=add,echo,ping deny=ok`.
2. Start the server live. Call each tool once: `ping` returns `pong`, `add(2, 3)` returns `5`, `echo` returns its input.
3. Show the deny: unknown tool `rm_rf` raises, never runs.

## Done when

Rich sees all three calls pass plus one deny. No new code. No new deps.

## Proof

`python packs/server-template/server.py --selftest` plus `node sprint/check.mjs` in `C:/Users/me/Desktop/mcp-forge` (vision FAILs on K-01 until Scorecard and steal map are filled; packs check is local only).
