---
role: builder
title: K-26 audit skips export output (scope to canonical files)
chain: start
---

Goal: K-26 DONE (R1): book2skill/audit.py skips export/ output (and skills/*/export/ generally) so audit counts canonical skill files only — audit 5650 tok/12 files must NOT grow to 14125 tok/30 files after x4 export rebuild (P1 2026-10-03-P1.md proof). Mirrors export.py:_own_output_ignore (skip output dir during walk).
Scope: book2skill/audit.py (walk skip only) + ONE regression test (export/ with dupe files excluded from counts). No other pipeline files. NOTE export/ is now gitignored (owner fd0febc) — build the test fixture under %TEMP%, not in skills/.
Proof: audit on skills/progit-branching reports pre-export counts with export-like dupes excluded + `python -m pytest tests/ -q` green (expect 22 passed: 21 + 1 new).
Stop: S/M 30 min. End with the RESULT line.
Record: K-26 [AUDIT-SKIP-EXPORT-1001] | audit skips export/, counts canonical, pytest 22 passed
Board: sprint/board.md K-26 READY -> DONE needs judge PASS + commit by lead.
