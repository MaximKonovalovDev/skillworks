---
role: builder
title: enforce eval 0.6 gate in export CLI (ships failing skills today)
---

Goal: `export` refuses to ship a skill whose eval pass rate is below 0.6, per AGENTS.md rule 2 and VISION R2, instead of silently shipping it.

Scope: `book2skill/cli.py` export command + `book2skill/export.py` wiring + one test in `tests/test_pipeline.py`. No README change.

Proof (pilot-view-r2, 2026-10-03):
- Built scratch skill `skills/pilot-view-demo`, eval rate **0.333** (`total 3, passed 1`).
- `python -m book2skill export --skill skills/pilot-view-demo --target claude --out dist/pilot-view-demo` → exit 0, skill copied. Gate never fired.
- Root cause: `cli.py:94` calls `export_mod.export(Path(skill), target, Path(out))` with `eval_report=None`, and `export.py:14` skips the gate when the report is `None`. The gate exists only as dead code on the CLI path (builder-r1 honored it by hand, not by enforcement).
- Suggested fix: export resolves the skill's latest eval report (or takes `--qa`/`--work` and runs eval inline) and refuses below 0.6 with `Error: eval gate refused export: rate ...`. Keep the manual-override story explicit if the loop wants one — today there is none, so failing skills ship by default.
- `python -m pytest tests/ -q` → 7 passed before change (baseline).

User sees differently: `export` on a sub-0.6 skill fails with a clear gate message telling them to fix the skill first, instead of producing a `dist/` bundle that looks shippable.

Stop: M 30 min for the packet; fix sized S. Proof for DONE: failing-rate skill refused via CLI + `python -m pytest tests/ -q` green with a new gate test.
