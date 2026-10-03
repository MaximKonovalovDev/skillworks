---
role: builder
title: K-24 pipe-run skill (cost cap + dry-run, headless)
chain: start
---

Goal: K-24 DONE (R1): skills/pipe-run/ — one-file pipeline with cost cap and dry-run, headless (OpenClaw lobster steal, repeatable batch runs). Mirror K-23's shape (SKILL.md frontmatter name matches dir + script + references/ + test proving cap enforced + dry-run clean).
Scope: skills/pipe-run/ (new dir only) + tests/test_pipe_run.py (new file only). No other skills, no pipeline code changes (new lane only; shared helper only if additive + tested).
Proof: skills/pipe-run/SKILL.md + test PASS (over-cap refused with spend quoted, dry-run changes nothing, under-cap runs) + `python -m pytest tests/ -q` green (expect 21 passed: 20 + 1 new).
Stop: M 40 min, end-to-end (skill + test + proof). End with the RESULT line.
Record: K-24 [PIPE-COST-1001] | pipe-run skill + cost-cap test, pytest 21 passed
Board: sprint/board.md K-24 READY -> DONE needs judge PASS + commit by lead.
