---
role: judge
title: review K-24 pipe-run skill (cost cap + dry-run + test)
---

Goal: Judge builder K-24 (skills/pipe-run/: SKILL.md name matches dir + scripts/pipe_run.py cost-cap/dry-run + references/cost-model.md + tests/test_pipe_run.py) for commit. Serves R1.
Scope: skills/pipe-run/ (new dir only) + tests/test_pipe_run.py (new file only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 21 passed); over-cap case exit 2 with spend quoted + no out dir; dry-run writes nothing; under-cap RUN writes receipt.json; confirm out-outside-input rule + exit codes documented.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-24 [PIPE-COST-1001] | pipe-run skill + cost-cap test, pytest 21 passed
Result: K-24 RESULT DONE 2026-10-03
