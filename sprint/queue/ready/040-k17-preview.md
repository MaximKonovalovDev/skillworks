---
role: builder
title: K-17 skill_preview tool (inspect-before-install)
chain: start
---

Goal: K-17 DONE (R3): skill_preview tool in mcp_server/server.py (README-then-SKILL.md fallback, inspect-before-install / Vol 0 sample). Baseline server.py now 196+ lines with INPUT_SCHEMA + skills-dir (K-29/015 DONE) — add preview following the same validation/envelope patterns.
Scope: mcp_server/server.py (preview tool + schema + validation only) + tests/test_mcp_schema.py or new test file (preview returns SKILL.md head; missing skill -> is_error unknown-skill envelope). No other files.
Proof: handshake + skill_preview progit-branching returns SKILL.md head + missing skill is_error + `python -m pytest tests/ -q` green (expect 27 passed: 26 + 1 new).
Stop: S/M 30 min. End with the RESULT line.
Record: K-17 [S01-C3] | skill_preview + test, pytest 27 passed
Board: sprint/board.md K-17 READY -> DONE needs judge PASS + commit by lead.
