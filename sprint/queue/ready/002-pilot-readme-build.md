---
role: builder
title: fix README build command (missing --name/--description)
---

Goal: A stranger copies the README `build` line and gets a working skill instead of `Error: Missing option '--name'`.

Scope: `README.md` only (one line). Proof copy-paste below. No code changes.

Proof (pilot-view-r2, 2026-10-03):
- README says: `python -m book2skill build --work work/mybook --skill skills/mybook`
- Actual CLI (`book2skill/cli.py:53-58`) requires `--work --skill --name --description`.
- Ran verbatim shape on scratch source: `python -m book2skill build --work work/pilot-view --skill skills/pilot-view-demo` → exit 2 `Error: Missing option '--name'.`
- With `--name pilot-view-demo --description "..."` → exit 0 `built skills\pilot-view-demo`.
- `python -m pytest tests/ -q` → 7 passed (pre-existing suite, still green).

User sees differently: the README Use block becomes copy-paste runnable:
`python -m book2skill build --work work/mybook --skill skills/mybook --name mybook --description "..."`.

Stop: M 30 min. One-line doc fix; verify by pasting the new line.
