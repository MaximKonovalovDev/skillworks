---
role: judge
title: review K-15/K-19 ranked skill_search
---

Goal: Judge builder K-15/K-19 (server.py EVAL_GATE + _parse_skill_frontmatter + _skill_meta rank/trust fields + gate-first sort + tests/test_mcp_rank.py ordering test) for commit. Serves R3. Ideas-only donor patterns — verify no pasted registry code; numbers derived locally (downloads=passed-count etc.).
Scope: mcp_server/server.py (rank hunks only) + tests/test_mcp_rank.py (new only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 31 passed); live stdio: progit (1.0, verified) before freud (0.5, unverified) with all 10 fields; validation/envelope/preview/skills-dir intact.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-15/K-19 [ranked search] | fields + gate-first sort + test, pytest 31 passed
Result: K-15/K-19 RESULT DONE 2026-10-03
