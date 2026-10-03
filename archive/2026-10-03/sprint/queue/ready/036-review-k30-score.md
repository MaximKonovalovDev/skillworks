---
role: judge
title: review K-30 part-score script (real data only)
---

Goal: Judge builder K-30 (tools/part_score.py 6 lines P1-P5+workspace from live artifacts + tests/test_part_score.py smoke test) for commit. Serves all rows. NOTE: builder reported a transient SyntaxError mid-run, fixed before green — verify the committed file parses clean + all numbers trace to real artifacts (UNKNOWN where unmeasured, no invented numbers).
Scope: tools/part_score.py (new only) + tests/test_part_score.py (new only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 26 passed); run `python tools/part_score.py` (exit 0, >=6 lines, six part markers); spot-check 2 numbers against their artifacts (e.g. freud chars vs work/freud-dreams, eval rates vs eval reports).
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-30 [TEAM-LOOP-1010-A] | part-score script, real data, pytest 26 passed
Result: K-30 RESULT DONE 2026-10-03
