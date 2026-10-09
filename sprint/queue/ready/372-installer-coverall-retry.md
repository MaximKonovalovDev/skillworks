---
role: pilot
title: installer cover-all retry after crash (resume-safe)
---
Goal: finish what the crashed cover-all run started: the 4 bumped skills (bash-allowlist v1.2.0, read-offset-guard v1.4.0, edit-verify v0.3.0 re-proved, bash-spawn-guard v1.4.0) installed in every using repo, with fresh 48 h clocks and a loads recount. Resume-safe: the crashed run claimed nothing and touched nothing, but verify state first anyway.

Scope: `python tools/install_fleet_skills.py` only, the private adopted.csv, scratch trial dirs under `$env:TEMP\opencode\`. Read-only in target repos (install paths only). Never commit or push, never touch halt or STOP files.

Proof:
- First `python tools/install_fleet_skills.py --check` per skill (or the seat's check command): paste each `ok <skill>: copy matches the source` line; install only what is missing or stale, and say which were already current.
- `python tools/fleet_failures.py compare bash-spawn-guard` plus `bash-allowlist` plus the offset/edit classes: paste before/now lines starting the fresh 48 h clocks.
- Stranger trial on the least-covered skill: `python tools/skill_trial.py grade --skill <name>` runs with/without plus lift RESULT PASS.
- `python tools/fleet_failures.py lanes`: paste the install wait line (was 8 wait).
- `node sprint/check.mjs` PASS.

Stop: 30 min. A repo that cannot be reached is named and skipped, never a stall; the second identical failure ends that repo's step. Claim this packet in `sprint/queue/claims.txt` first (`INSTALL-COVERALL-RETRY | pilot-installer | <UTC> | all-using-repos`). End with `RESULT: DONE - <what installed where, clocks started> | proof: <check plus lanes lines>` or `RESULT: PARTIAL - <what is missing and where> | proof: <lines you have>`.
