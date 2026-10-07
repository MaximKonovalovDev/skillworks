---
role: judge
title: review auditfold gates repair
chain: review
of: builder-fix-auditfold-repair
writer: builder
attempt: 1
origin_title: repair auditfold gates reader (O-008)
---
Review builder-fix-auditfold-repair, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-fix-auditfold-repair.md (verify it exists; else BLOCKED). Rerun its proofs yourself, read its diff, check O-008's done-when as written. You never edit. Scope: book2skill/gates.py frontmatter reader plus audit.py plus the two test files; skills/git-one-branch must be untouched; SKILL_LIVE lines (gates.py:18, 80-86) must be intact; concurrent dirt out of scope.

Run the check that fits what it made, and paste the result line of each:
1. `python -m book2skill audit --skill skills/git-one-branch` prints 0 flags containing 2 chars; a deliberately broken skill still fails (gate intact).
2. The fleet format test for git-one-branch (find by grep `description is`): green.
3. `pytest tests/test_audit_grades.py -q` green; `node sprint/check.mjs` PASS.

Always: (a) full pytest equal or better than before (pre-existing out-of-scope fails named, not charged); (b) nesting guard clean; (c) privacy: no other repo's path, text or number, no secret; (d) only owned files changed; (e) ONE REAL THING: the format test flipped from red to green on this diff.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Repair result, cut:
<task_result> RESULT: DONE - gates.py frontmatter folds >-/| block scalars like audit.py (git-one-branch desc reads 477 chars, format test green) plus a fold regression test | proof: test_fleet_skill_format[git-one-branch] passes; audit shows 0 lines matching '2 chars'; pytest 656 passed with only 6 pre-existing unrelated failures; node sprint/check.mjs 20/0/0 </task_result>

Keeper facts: run builder-fix-auditfold-repair (seat builder, @builder), repair auditfold gates reader (O-008).
