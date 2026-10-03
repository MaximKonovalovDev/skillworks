---
role: judge
title: review builder-rows-r1 (K-04 seeds)
---

Goal: Judge builder-rows-r1 K-04 (2 books to 2 skills, eval QA logged) for commit.
Scope: skills/freud-dream-psychology/, skills/progit-branching/, evals/seeds_qa.jsonl, evals/freud-dreams_qa.jsonl, evals/progit-branching_qa.jsonl, work/ quarantine check (gitignored, never committed).
Proof: rerun `python -m pytest tests/ -q` yourself plus the row done-when (2 skills with eval rates logged, pytest green); verify SKILL.md frontmatter name==dir, Sources license lines, work/ not staged.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: builder-rows-r1 | skills/freud-dream-psychology SKILL.md + evals/seeds_qa.jsonl (freud 0.50, progit 0.92) + pytest 7 passed
Result: sprint/queue/done/builder-rows-r1.md RESULT DONE 2026-10-03
