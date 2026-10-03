---
name: cron-skip-clean
description: Durable file timer that skips when clean. Use for headless cron ticks over a watched dir when rerunning unchanged work wastes tokens; RUN on change, SKIP when the fingerprint matches.
---

# cron-skip-clean

Skip when clean, run when dirty. Headless: no phone, no network, no
prompts. Fingerprint a watch dir, compare against a durable state file.

## Use it

```powershell
python skills/cron-skip-clean/scripts/cron_skip_clean.py --watch <dir> --state <state.json>
```

- First run (or changed dir): prints `RUN <fp>`, refreshes the state file.
- Unchanged dir: prints `SKIP clean <fp>`, touches nothing.
- Missing/unparseable state file counts as dirty (one RUN, then clean).

Keep the `--state` file outside the `--watch` dir. State schema and
recovery rule live in `references/state-format.md`.
