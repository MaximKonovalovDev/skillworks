# mcp-template proof

Selftest: `python selftest.py` prints `SELFTEST PASS`.

Tools (3):
- ping: liveness check, returns pong.
- add(a, b): adds two numbers. 2+3=5.
- echo(text): returns text back.

Guard verdict: PASS. Duplicate `ping` rejected, original kept. Stderr warns, no overwrite.
