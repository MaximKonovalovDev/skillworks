---
role: builder
title: fix README eval command (missing --work)
---

Goal: A stranger copies the README `eval` line and gets a pass-rate report instead of `Error: Missing option '--work'`.

Scope: `README.md` only (one line). Proof copy-paste below. No code changes.

Proof (pilot-view-r2, 2026-10-03):
- README says: `python -m book2skill eval --skill skills/mybook --qa evals/sample_qa.jsonl`
- Actual CLI (`book2skill/cli.py:71-77`) requires `--work --skill --qa`.
- Ran verbatim shape: `python -m book2skill eval --skill skills/pilot-view-demo --qa evals/sample_qa.jsonl` → exit 2 `Error: Missing option '--work'.`
- With `--work work/pilot-view` added → exit 0, report `{"total": 3, "passed": 1, "rate": 0.333...}`.
- `python -m pytest tests/ -q` → 7 passed (still green).

User sees differently: the README Use block becomes copy-paste runnable:
`python -m book2skill eval --work work/mybook --skill skills/mybook --qa evals/sample_qa.jsonl`.

Stop: M 30 min. One-line doc fix; verify by pasting the new line.
