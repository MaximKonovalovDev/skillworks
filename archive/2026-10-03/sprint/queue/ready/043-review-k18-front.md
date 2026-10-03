---
role: judge
title: review K-18 versioned frontmatter
---

Goal: Judge builder K-18 (_frontmatter emits version 0.1.0 default + author + tags after name+description, NAME_RULE intact + 1 tmp-rebuild test) for commit. Serves R5.
Scope: book2skill/build.py (_frontmatter only) + tests/test_build_frontmatter_version.py (new file only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 28 passed); _frontmatter order name->description->version->author->tags; NAME_RULE mismatch still exit 2 (K-36 intact); no seed/skill files changed.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-18 [S01-C4] | versioned frontmatter + test, pytest 28 passed
Result: K-18 RESULT DONE 2026-10-03
