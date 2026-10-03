---
role: builder
title: K-20 fingerprint rescan single-flight refresh
chain: start
---

Goal: K-20 DONE (R1): single-flight refresh no-ops when chunk fingerprint matches (ideas-only donor pattern). Baseline book2skill/index.py + book2skill/refresh.py have no guard/receipt.
Scope: book2skill/refresh.py (guard + receipt only; index.py only if a fingerprint getter is missing) + ONE test (twice-run refresh: second run no-ops with receipt). Fixture under %TEMP%. No other files.
Proof: twice-run refresh second run no-ops with receipt + `python -m pytest tests/ -q` green (expect 29 passed: 28 + 1 new; parallel lane may move baseline — report actual).
Stop: S/M 30 min. End with the RESULT line.
Record: K-20 [S02-C4] | single-flight refresh + test, pytest green
Board: sprint/board.md K-20 READY -> DONE needs judge PASS + commit by lead.
