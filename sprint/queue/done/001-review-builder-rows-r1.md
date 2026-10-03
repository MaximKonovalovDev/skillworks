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


## Result (completed)

<task id="ses_f0017c4f4ffeGR9wzAQum9HreD" state="completed">
<task_result>
Changed: 2 skills + evals already tracked (commit 4549734); work/ ignored, no staged changes.
Before: claim pytest 7 passed, freud 0.50/progit 0.92, progit "not exported".
After rerun: `python -m pytest tests/ -q` → 11 passed (green, count drift).
After file check: frontmatter name==dir OK both; Sources license+quarantine lines OK; work/ ignored, not staged OK.
After log check: `evals/seeds_qa.jsonl` shows freud 0.5 but progit 1.0 (12/12), not claimed 0.92 — rate mismatch.
After scope check: FAIL — untracked recursive `skills/progit-branching/export/...` nesting contradicts "not exported"; unstaged deletions `sprint/halt`, `ready/001-review...` outside scope.
Revert (read-only, not run): `Remove-Item -Recurse skills/progit-branching/export; git checkout -- sprint/halt sprint/queue/ready/001-review-builder-rows-r1.md`
VERDICT: FAIL

</task_result>
</task>
