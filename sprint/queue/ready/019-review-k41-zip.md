---
role: judge
title: Review K-41 STEAL-ZIP (export writes out/<target>/<name>.zip)
---

Goal: Independent review of the builder's K-41 DONE (chain: start) before the lead commits: `book2skill/export.py` `_write_zip` + `tests/test_export_zip.py`.

Scope: `book2skill/export.py` diff, `tests/test_export_zip.py`, row K-41 done-when in `sprint/board.md`. No code changes by the judge.

Proof: re-run `python -m pytest tests/test_export_zip.py -q` and `python -m pytest tests/ -q` yourself; check SKILL.md-at-root, dotfile skip, gate-refusal-writes-no-ZIP, no nesting under `--out` inside skill; confirm gate arithmetic `rate < 0.6` untouched. At most 15 lines: PASS (lead may commit by path) or FAIL (one repair back to the builder, exact lines).

Stop: S 20 min. End: `RESULT: PASS|FAIL - <one line> | proof: <commands>`.
