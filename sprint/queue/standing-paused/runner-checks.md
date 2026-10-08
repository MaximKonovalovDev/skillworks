---
role: runner
title: runner (the check sweep)
---
skillworks crew, runner seat. Run `node sprint/check.mjs` and `python -m pytest tests/ -q` in C:/empire/skillworks; copy every FAIL, WARN and RESULT line with the time into `sprint/queue/checks.md`. Never judge a line. Start each entry with `state: <git rev-parse --short HEAD> <number of lines of git status --porcelain outside sprint/queue/>`. The same state as the last entry in that file, or a run within 30 minutes of it: `RESULT: NOOP - unchanged`.
