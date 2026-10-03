---
role: judge
title: review 015 skills-dir override + unknown-skill reply (server.py)
---

Goal: Judge builder-015 (--skills-dir flag + $SKILLWORKS_SKILLS_DIR/$SKILLS_DIR + unknown-skill isError envelope naming served dir + tests/test_mcp_skills_dir.py + 1 README line) for commit. Depends on K-29 PASS (stacked in server.py — if K-29 FAILs, hold this too).
Scope: mcp_server/server.py (skills-dir resolution + unknown-skill reply only) + tests/test_mcp_skills_dir.py (new) + README.md (1 documented line).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 19 passed); out-of-tree scratch skill returns hits via --skills-dir; unknown skill names served dir in envelope; K-29 schema behavior intact.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: 015-pilot-mcp-scratch-invisible | skills-dir override + unknown-skill reply, pytest 19 passed
Result: 015 RESULT DONE 2026-10-03
