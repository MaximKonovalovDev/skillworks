---
role: builder
title: persist eval report so README-order export passes the gate
---

Goal: A stranger who runs the README lines in order (eval passes, then export)
gets a shipped bundle instead of `eval gate refused export: no eval report found`.

Scope: `book2skill/eval.py` (save `eval_report.json` beside the skill) and/or
`README.md` export line (document `--work/--qa` inline). Sized S. No test-book
commits; `work/` stays gitignored.

Proof (pilot-view-r10, 2026-10-03, stranger run from clean start):
- `python -m pytest tests/ -q` → 9 passed.
- README `build` line (with `--name/--description`) → exit 0; `eval` line
  (with `--work`) → exit 0. 002 + 003 VERIFIED fixed.
- Scratch skill at rate 0.0: `export` without flags → refused "no eval report";
  with `--work/--qa` → refused "rate 0.000 below 0.6". 004 VERIFIED fixed.
- `export --target bogus` → exit 2 clean usage error, no traceback.
  005 VERIFIED fixed.
- MCP stdio: handshake + `tools/list` + `skill_search "branching git pointer"`
  → progit-branching (score 43); `"dream interpretation freud"` →
  freud-dream-psychology (score 658). K-04 VERIFIED served.
- STILL FAILS: `eval --work work/progit-branching --skill skills/progit-branching
  --qa evals/progit-branching_qa.jsonl` → rate 1.0, but no
  `skills/progit-branching/eval_report.json` is written (`eval.py:run_eval`
  prints only; `Test-Path` → False). The very next README line,
  `export --skill skills/progit-branching --target claude --out dist` →
  exit 1 `eval gate refused export: no eval report found`, although eval
  just passed. Only the `--work/--qa` inline form passes the gate.
- Scratch dirs (`work/pilot-r10`, `skills/pilot-r10-demo`, `dist/`) removed
  after the run; repo left clean.

User sees differently: after a passing eval, the plain README `export` line
ships the skill (report found, rate above gate) instead of telling a user who
just ran eval to "run eval first".

Stop: M 30 min. Proof for DONE: README-order eval→export on progit-branching
ships to `dist/` + `python -m pytest tests/ -q` green with a persistence test.
