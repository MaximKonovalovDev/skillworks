---
role: judge
title: review K-25 inbox-file-reader skill (isolated, no code touch)
---

Goal: Judge builder K-25 (skills/inbox-file-reader/: SKILL.md name matches dir + file_one_item.py allowlist paths + references/isolation.md + tests/test_inbox_file_reader.py) for commit. Serves R1.
Scope: skills/inbox-file-reader/ (new dir only) + tests/test_inbox_file_reader.py (new file only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 23 passed); one item filed to `- [ ]` board line verbatim; .py/code paths refused (exit !=0 or refusal message); confirm script cannot write outside the two allowlisted paths.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-25 [INBOX-READER-1001] | inbox reader skill + file-one-item test, pytest 23 passed
Result: K-25 RESULT DONE 2026-10-03
