---
role: judge
title: review K-23 cron-skip-clean skill (SKILL.md + script + test)
---

Goal: Judge builder K-23 (skills/cron-skip-clean/: SKILL.md frontmatter name matches dir + scripts/cron_skip_clean.py sha256 fingerprint + references/state-format.md + tests/test_cron_skip_clean.py RUN->SKIP->dirty->RUN cycle) for commit. Serves R1.
Scope: skills/cron-skip-clean/ (new dir only) + tests/test_cron_skip_clean.py (new file only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 19 passed); run the script twice on a scratch dir (RUN then SKIP clean same fp), touch a file (RUN new fp); confirm state-outside-watch-dir + exit 0 contract.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-23 [CRON-SKIP-1001] | cron-skip-clean skill + skip-on-clean test, pytest 19 passed
Result: K-23 RESULT DONE 2026-10-03
