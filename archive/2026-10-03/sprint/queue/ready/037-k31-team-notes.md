---
role: planner
title: K-31 team notes + owner seats (<=1KB each)
---

Goal: K-31 DONE (all rows): team/<part>.md notes (P1-P5 + workspace, each <=1024 B: tried, moved, failed) + one owner seat aim per part at the part score (from tools/part_score.py output, run it).
Scope: team/*.md (6 files, <=1KB each) + sprint/board.md K-31 evidence line. No code.
Proof: `wc -c team/*.md` all <=1024 + `node sprint/check.mjs` PASS + scores quoted from a live part_score.py run.
Stop: S/M 30 min. End with the RESULT line.
Record: K-31 [TEAM-LOOP-1010-B] | team notes + owner seats, check PASS
Board: sprint/board.md K-31 READY -> DONE needs lead verify (planner work, no judge chain) + commit by lead.
