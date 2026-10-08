---
role: judge
title: review doctor scout row plus sheet (DR-1007-16)
chain: review
of: researcher-doctor-scout-6
writer: researcher
attempt: 1
origin_title: scout next failure class (doctor lane)
---
Review researcher-doctor-scout-6. Its record: C:\empire\skillworks\sprint\queue\done\researcher-doctor-scout-6.md (if missing, judge the tree and say so). Its row DR-1007-16 is on sprint/board.md; its sheet is evals/read-abort-1007d_trials.jsonl. You never edit.

Check and paste each: the row opens with a lane tag, names its Scorecard row, carries F2P plus P2P, has no pipe character inside a cell; the class has no other open row and is not a DONE repeat (spot-check board plus board-archive plus git log, especially DR-1007-11 v0.2.0 DONE f4906a1 plus DR-1007-13 v0.3.0 DONE d08e35d: this must be a distinct still-failing count after 0 loads, not a re-row); the sheet exists with 12 task ids; `node sprint/check.mjs` PASS after the board edit.

Always: only board plus evals plus queue records changed; no secret; ONE REAL THING: a real uncovered class with a dated count, or FAIL paperwork (re-row of a DONE read-abort bump is FAIL).

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after, and how to revert it. A proof you cannot run is BLOCKED, never a guess.
