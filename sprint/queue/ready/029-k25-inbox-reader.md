---
role: builder
title: K-25 inbox-file-reader skill (isolated triage, no code touch)
chain: start
---

Goal: K-25 DONE (R1): skills/inbox-file-reader/ — tiny isolated reader that files one inbox item to a board empire-inbox file, never touches code (OpenClaw isolated reader steal, autonomous triage). Mirror K-23/K-24 shape (SKILL.md name matches dir + script + references/ + test).
Scope: skills/inbox-file-reader/ (new dir only) + tests/test_inbox_file_reader.py (new file only). Script reads ONLY the given inbox file + writes ONLY the given board file (allowlist paths); test proves one item filed correctly + code files untouched (refuses paths outside the two).
Proof: skills/inbox-file-reader/SKILL.md + test PASS (one item filed, correct board line, no code touched) + `python -m pytest tests/ -q` green (expect 22 passed: 21 + 1 new).
Stop: M 40 min, end-to-end (skill + test + proof). End with the RESULT line.
Record: K-25 [INBOX-READER-1001] | inbox reader skill + file-one-item test, pytest 22 passed
Board: sprint/board.md K-25 READY -> DONE needs judge PASS + commit by lead.
