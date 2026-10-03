---
role: builder
title: K-07 redo - clean export x4, remove nested scratch
---

Goal: K-07 DONE for real: progit-branching exported to all 4 targets with per-target layout check, no nesting, serving R5 export targets (weakest row, 0%).
Scope: skills/progit-branching/export/ (remove first, fully), book2skill/export.py + cli.py ONLY if export recurses into its own output dir (fix: skip output dir during copy); tests only if a regression test is added for no-nesting. No README, no other skills.
Proof: `python -m book2skill export` (README order after eval) to claude|codex|opencode|gemini under skills/progit-branching/export/ -> 4 dirs each with SKILL.md, `Get-ChildItem -Recurse` shows NO export-in-export nesting, `python -m pytest tests/ -q` green. Show before (nested garbage from interrupted r13 run + backup 9c2f7e1) vs after (flat 4-target tree).
Stop: M 45 min; end-to-end (remove, fix cause if code, re-export x4, verify). End with the RESULT line.
Record: K-07 [WEAKEST-R5-1001] redo | export/ nested scratch (9c2f7e1) -> clean 4-target tree
Board: sprint/board.md K-07 READY -> DONE needs judge PASS + commit by lead.
