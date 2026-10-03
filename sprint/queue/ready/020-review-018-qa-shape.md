---
role: judge
title: Review 018 QA-shape refusal (eval.py validate_qa + make.py early exit 2)
---

Goal: Independent review of the builder's 018 DONE before the lead commits: `book2skill/eval.py` `_check_item`/`validate_qa` + `book2skill/make.py` early refusal + `tests/test_make.py` wrong-shape test.

Scope: `book2skill/eval.py` diff, `book2skill/make.py` diff, `tests/test_make.py` new test, packet `018-pilot-make-qa-shape-crash.md`. No code changes by the judge.

Proof: re-run `python -m pytest tests/test_make.py -q` and `python -m pytest tests/ -q` yourself; check wrong-shaped QA exits 2 with shape quoted and no traceback, correct-shaped QA still builds, gate arithmetic `rate < 0.6` untouched, no other files touched. At most 15 lines: PASS (lead may commit by path) or FAIL (one repair back to the builder, exact lines).

Stop: S 20 min. End: `RESULT: PASS|FAIL - <one line> | proof: <commands>`.
