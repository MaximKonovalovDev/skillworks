---
role: builder
title: adopt mcp server template as tested pack (PIPE-1006-1)
chain: start
attempt: 1
---
Goal: serve PIPE-1006-1. Read research/folded-mcp-forge/ (MCP server template plus notes, donor modelcontextprotocol python-sdk MIT) and adopt the server template as a tested pack: template runs with a test, pack listed in the catalog. Check the board row PIPE-1006-1 for F2P plus P2P.

Scope: research/folded-mcp-forge/ (read-only), packs/mcp-template/ (exists untracked, claim it), the pack test, the catalog listing file. Own paths only, never commit.

Proof: the template server selftest ends SELFTEST PASS; the pack is listed in the packs catalog with test green; `node sprint/check.mjs` PASS; MIT only, no other repo's text or numbers.

Stop: M 30 min. Claim: append `PIPE-1006-1 | builder-pack-mcp | <UTC> | packs/mcp-template/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. Write `sprint/queue/done/builder-pack-mcp.md` with the RESULT plus proof lines before replying (no record, no review). End with the RESULT line.
