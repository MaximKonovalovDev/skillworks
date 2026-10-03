---
role: builder
title: K-30 part-score script (one line per part from real data)
chain: start
---

Goal: K-30 DONE (all rows): tools/part_score.py prints one line per part (P1-P5 + workspace) from REAL data (receipts, eval rates, MCP handshake, shop proof) — first self-developing-loop instrument (K-22 child A).
Scope: tools/part_score.py (new file only) + ONE smoke test (script exits 0 + prints >=6 lines; real-data only, no invented numbers — UNKNOWN where unmeasured). No other files.
Proof: `python tools/part_score.py` prints one line per part + `python -m pytest tests/ -q` green (expect 24 passed: 23 + 1 new).
Stop: S/M 30 min. End with the RESULT line.
Record: K-30 [TEAM-LOOP-1010-A] | part-score script, real data, pytest 24 passed
Board: sprint/board.md K-30 READY -> DONE needs judge PASS + commit by lead.
