---
role: runner
title: K-12 measure the bar (time extract-to-export per stage)
---

Goal: K-12 DONE (R1): time extract-to-export end to end on work/progit-branching, receipted per stage — the G2 bar measurement.
Scope: NO code. Run each stage timed (Measure-Command) on work/progit-branching in %TEMP% copies where writes happen (never commit work/ — gitignored); write the timing table into sprint/board.md K-12 Evidence cell + report it. Verify receipts carry counts.
Proof: timing table (8 stages, seconds each, total) in K-12 Evidence + `python -m pytest tests/ -q` green (expect 30 passed, unchanged) + `node sprint/check.mjs` PASS.
Stop: S/M 30 min. End with the RESULT line.
Record: K-12 [G2-BAR-1001] | timing table in Evidence, pytest 30 passed
Board: sprint/board.md K-12 READY -> DONE needs lead verify (measurement, no judge chain) + commit by lead.
