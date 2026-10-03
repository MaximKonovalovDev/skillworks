# State format

`cron_skip_clean.py` keeps one JSON file (default caller-chosen `--state`
path, e.g. `work/cron-skip-clean/state.json`):

```json
{"fingerprint": "9f2c…", "tool": "cron-skip-clean", "version": 1}
```

- `fingerprint`: sha256 (truncated to 16 hex chars) over the sorted
  relative paths plus full file bytes of the `--watch` dir.
- A missing or unparseable state file counts as dirty: the run prints
  RUN and rewrites the file. Never hand-edit it; delete it to force
  one RUN on the next tick.
- The state file must live outside the `--watch` dir, otherwise the
  fingerprint would chase itself and never skip.
