---
role: builder
title: repair allowlist v1.2.0 after FAIL review
---
Goal: answer the FAIL on 366-cure-allowlist-v12-review with tree truth, not new scope. The skill shape holds (grade 22 runs 1.0/0.0 lift 1.0); the FAIL charges suite drift, unmet 48 h halving, and 16 changed files outside the owned set.

Scope: `skills/bash-allowlist/`, `evals/bash-allowlist_trials.jsonl`, `tests/test_bash_allowlist.py`, `team/p3.md` only. Read-only everywhere else. Never commit or push.

Proof:
- `git status --short` plus `git diff --stat`: name every file the v1.2.0 bump touched vs pre-existing drift (book2skill/build.py, index.py, tools/* were M before the cure claim 2026-10-09T05:08Z). Revert with `git checkout --` anything the bump itself changed outside the owned set; leave other sessions' drift alone and name it.
- Re-run and paste: `python tests/live_proof.py bash-allowlist` ends proven; `python tools/skill_lint.py check --skill skills/bash-allowlist` exit 0; `python tools/skill_trial.py grade --skill bash-allowlist` runs with/without plus lift; `python -m pytest tests/test_bash_allowlist.py tests/test_fleet_skills.py -q` green; `node sprint/check.mjs` PASS.
- Full-suite honesty: run `python -m pytest tests/ -q` once only if time remains in the box; else paste the named FAILED lines from the review (export-guard, c02, stale proofs) and show none traces to skills/bash-allowlist/.
- Halving honesty: class reads UP 520 to 933 per pilot1009; halving needs adoption plus 48 h and cannot pass same-day. Say so in one line; do not fake it.

Stop: M 25 min. End with `RESULT: DONE - repair <what is true now> | proof: <live plus grade one-liners>` or `RESULT: BLOCKED - halving needs adoption plus 48 h | proof: <compare line>`. Second FAIL comes to the lead, not a second repair.
