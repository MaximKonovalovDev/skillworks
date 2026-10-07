---
role: builder
title: record auditfold repair result (O-008)
chain: repair
of: builder-fix-auditfold-repair
writer: builder
attempt: 2
origin_title: fix book2skill audit folded-YAML misread (O-008)
---
The judge blocked the repair review: `sprint/queue/done/builder-fix-auditfold-repair.md` was never written, so there was nothing to judge. The repair work itself is in the tree (a later review saw the gates.py folding live). No code changes in this packet.

Goal: verify the repair diff is present and write the missing record. Steps: (1) confirm `book2skill/gates.py` frontmatter reader folds `>-`/`|` (around lines 158-166) and `python -m book2skill audit --skill skills/git-one-branch` prints 0 lines matching 2 chars; (2) confirm the fleet format test for git-one-branch passes and skills/git-one-branch is untouched; (3) write `sprint/queue/done/builder-fix-auditfold-repair.md` containing the RESULT line plus the proof lines (audit output, format test, audit_grades tests, check.mjs). If any check fails, say so in the RESULT instead of writing a green record.

Scope: read-only except the one done-record file. Never commit.

Stop: m 15 min. End with the RESULT line.
