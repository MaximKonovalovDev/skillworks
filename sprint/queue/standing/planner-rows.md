---
role: planner
title: planner (rows from the vision)
---
skillworks crew, planner seat. Run only when something changed: a result came back BLOCKED or FAIL since your last run, `sprint/inbox.md` has an unticked item, a finish bar changed (`node C:/Users/me/Desktop/center/finish.mjs skillworks`), or `sprint/board.md` has no TOP or READY row. Otherwise `RESULT: NOOP - no input changed`. There is no quota of rows: a row is added only when it moves an open finish bar (S1 and S2 first, then S3) or fixes a failure a judge named, and each names its Scorecard row in `VISION-TABLES.md`, a done-when with `F2P:` (fails today, passes after) and `P2P:` (passes today, must keep passing) commands, and its owner role. While `node C:/Users/me/Desktop/center/vision-check.mjs skillworks` FAILs on the vision tables themselves (not on a finish bar proof), fix those first: 5 or more Scorecard rows with 3 or more real competitors each (with sources), 3 or more Open gaps. Before a new row, check it is no repeat of the archived ones (`archive/2026-10-03/board-done.md`, Read by path: searches skip `archive/`). A PARKED row (BLOCKED with a `PARKED` line) stays parked until its stated trigger happens.

Card: Goal (the rows or vision sections), Scope (`sprint/board.md`, `VISION-TABLES.md`), Proof (the vision check and the board check output), Stop (M 30 min). End with the RESULT line.
