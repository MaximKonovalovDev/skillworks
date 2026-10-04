---
name: cron-skip-clean
description: Skip a scheduled, looped or watched run when its input folder did not change, so unchanged work is not paid for twice. Use before a cron tick, loop round or watcher re-processes a folder; the script fingerprints the folder and prints RUN when it changed (or on the first run) and SKIP clean when it did not.
license: MIT
---

# cron-skip-clean

Skip when clean, run when dirty. Headless: no network, no prompts. It fingerprints a watch folder (file names and
file bytes) and compares the result with a state file it keeps.

## Use it

Run `scripts/cron_skip_clean.py` from this skill's folder, or give its full path:

```powershell
python scripts/cron_skip_clean.py --watch <dir> --state <state.json>
```

The first word of stdout is the answer:

- `RUN <fp>`: first run, or something in `--watch` changed, or the state file was missing or unusable. The state file is
  rewritten at once, BEFORE your work runs. Exit 0.
- `SKIP clean <fp>`: nothing changed. Nothing is written, not even the state file. Exit 0.
- `ERROR ...`: exit 2 and the state file is not touched. Causes: the watch folder is missing, a file in it cannot be
  read, or `--state` lies inside `--watch`.

In a loop script (pwsh):

```powershell
$tick = python scripts/cron_skip_clean.py --watch work/in --state C:/Users/me/.empire/state/in.json
if ($LASTEXITCODE -ne 0) { throw $tick }
if ($tick -like 'SKIP*') { return }
# the real work goes here
```

## Rules

- Put `--state` outside `--watch`. Inside it, the state file would change the fingerprint it holds, so every tick
  would RUN. The script refuses that pair (exit 2).
- A change means different bytes, a new or removed file, or a rename, in any subfolder. A new modified time with the
  same bytes is clean. A folder with no file in it is clean.
- The state is saved before your work runs. If the work fails, delete the state file to force one RUN on the next tick.
- It reads every file in `--watch` on every tick. Point it at the folder your work really reads, not at a whole repo.

State format, the exact fingerprint and recovery: `references/state-format.md`.
