---
role: builder
title: K-33 coach baseline + skill upkeep + kiasar credit
chain: start
---

Goal: K-33 DONE (all rows): (a) coach baseline — part scores exist 1 round only, no 3-flat history, so nothing to undo; record the baseline + the undo trigger rule in team/coach.md; (b) skill upkeep map — each part gets its skill from what works (P1 extract/audit skills TBD vs existing cron/pipe/reader + 2 seeds: map part->skill in the same note); (c) THIRD_PARTY_NOTICES.md += kiasar/gutenberg_cleaner MIT attribution line for the reimplemented marker-strip idea (K-28 follow-up from judge-018).
Scope: team/coach.md (new, <=1KB) + THIRD_PARTY_NOTICES.md (1 line) + sprint/board.md K-33 evidence. No code.
Proof: coach baseline states scores-run-count + undo trigger + part->skill map + credit line present + `python -m pytest tests/ -q` green (expect 26 passed, no new test — notes only).
Stop: S 20 min. End with the RESULT line.
Record: K-33 [TEAM-LOOP-1010-D] | coach baseline + upkeep map + credit, pytest 26 passed
Board: sprint/board.md K-33 READY -> DONE needs lead verify + commit by lead.
