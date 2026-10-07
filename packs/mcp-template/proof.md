# mcp-template proof

Selftest: `python selftest.py` prints `SELFTEST PASS` (run from `packs/mcp-template/`).
Server flag: `python server.py --selftest` prints `SELFTEST PASS`.
Pack test: `python -m pytest tests/test_mcp_template.py -q` green (5 tests).
Catalog: `packs/catalog.md` lists `packs/mcp-template` with this proof.
Donor: modelcontextprotocol python-sdk, MIT, read live 2026-10-06 per
`research/folded-mcp-forge/packs/w2-steal.md`; no donor code copied, original rewrite.

Tools (3):
- ping: liveness check, returns pong.
- add(a, b): adds two numbers. 2+3=5.
- echo(text): returns text back.

Guard verdict: PASS. Duplicate `ping` rejected, original kept. Stderr warns, no overwrite.
