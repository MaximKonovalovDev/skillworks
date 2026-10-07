---
role: builder
title: repair skiphint suite-green proof (O-006)
chain: repair
of: builder-fix-skiphint
writer: builder
attempt: 2
origin_title: fix pytest live-skip stranger hint (O-006)
---
The judge failed builder-fix-skiphint. Its verdict, cut:
<task_result> VERDICT: FAIL - Changed: book2skill/gates.py +7 lines only, O-006 F2P met, SKILL_LIVE=1 gives 18 passed, check 20/0/0. P2P not met: O-006 requires python -m pytest tests/ -q green; packet admits PARTIAL with 7 failed, my rerun timed out at 300s (concurrent dirty book2skill/audit.py out of scope, green unproven). </task_result>

Goal: prove the suite state, nothing else. Rerun `python -m pytest tests/ -q` (allow the long run, up to M 40 min total for this repair). If green, done. If red, prove every remaining failure is independent of this diff: for each failing test, show it fails identically with the diff stashed (`git stash -- book2skill/gates.py`, rerun just that test, unstash) or names a file this packet never touched. Do not fix other packets' files.

Scope: book2skill/gates.py only, read-only everywhere else. Own paths only, never commit.

Proof: the F2P rerun (hint line present without SKILL_LIVE, 18 passed with it) plus the suite verdict: either green, or the per-failure independence list with stash-proof lines pasted. End with the RESULT line.
