---
role: builder
title: repair auditfold gates reader (O-008)
chain: repair
of: builder-fix-auditfold
writer: builder
attempt: 2
origin_title: fix book2skill audit folded-YAML misread (O-008)
---
The judge failed builder-fix-auditfold. Its verdict, cut:
<task_result> VERDICT: FAIL - audit.py folds >- and | now, git-one-branch reads 477 chars with 0 2-chars flags, broken skill still fails, audit_grades 6 passed, check 20/0/0, arsenal 13/0/0. P2P fails: test_fleet_skill_format[git-one-branch] still description is 2 chars via book2skill/gates.py:163, the same fold bug in a second reader this packet was scoped away from. </task_result>

Lead scoping (binding, expanded): the second reader is in scope for this repair. Apply the same block-scalar folding to the frontmatter reader in book2skill/gates.py (around lines 158-166). Do not touch the SKILL_LIVE warning lines (gates.py:18, 80-86, O-006's packet owns them).

Goal: `python -m book2skill audit --skill skills/git-one-branch` 0 flags containing 2 chars AND the fleet format test for git-one-branch green. Add one regression test where the format test lives (find it by grep description is). skills/git-one-branch stays untouched.

Scope: book2skill/gates.py (frontmatter reader only), book2skill/audit.py if needed, tests/test_audit_grades.py plus the fleet format test file. Own paths only, never commit.

Proof: audit command 0 lines matching 2 chars; fleet format test for git-one-branch passes; deliberately broken skill still fails audit; python -m pytest tests/ -q and node sprint/check.mjs equal or better than before. End with the RESULT line.

Stop: M 30 min. One repair only.
