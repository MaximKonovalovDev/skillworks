---
role: builder
title: K-11 repair - fill 3 scaffold stubs from the book
chain: start
---

Goal: Repair K-11 FAIL (judge-056 PARTIAL): skills/james-psychology-briefer/cheatsheet.md + patterns.md + glossary.md are placeholder stubs (53/53/41B "Fill...") while siblings carry ~1.3KB real content. Fill all three FROM work/james-psychology-brieber/src.txt (James Briefer Course text): cheatsheet (5+ dated chapter-distinctive entries), patterns (3+ named patterns with chapter refs), glossary (5+ defined terms). No stubs, no placeholder data — depth rule.
Scope: skills/james-psychology-brieber/cheatsheet.md + patterns.md + glossary.md (content only). No other files, no QA/eval changes, no pipeline code.
Proof: all three files >500 B real book-derived content (siblings' scale) + `python -m pytest tests/ -q` green (expect 32 passed) + eval still 8/12=0.667 (content edits must not touch QA anchors — verify eval rate unchanged).
Stop: S 25 min. End with the RESULT line.
Record: K-11-repair [G3-EDGE-1001] | stubs filled from book, eval 0.667 intact, pytest 32 passed
Board: sprint/board.md K-11 READY -> DONE needs judge re-PASS + commit by lead.
