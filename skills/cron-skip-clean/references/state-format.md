# State format

`cron_skip_clean.py` keeps one JSON file, the `--state` path the caller chooses (for example
`work/cron-skip-clean/state.json`):

```json
{"fingerprint": "9f2c0a41d7be3358", "tool": "cron-skip-clean", "version": 1}
```

## The fingerprint

sha256, cut to the first 16 hex characters, over this byte stream:

1. Every file under `--watch`, in every subfolder, sorted by its relative path as a string (forward slashes, the same
   order on every operating system).
2. For each file: the relative path in UTF-8, one NUL byte, the full file bytes, one NUL byte.
3. At the end: the text `count=<number of files>`.

Only files count. Modified times do not count, so `touch` is clean. A folder with no file in it is clean. A rename, a
new file, a removed file or one changed byte is dirty.

## Recovery

- A missing, empty, binary, unparseable or wrong-shape state file (JSON that is not an object, or has no text
  `fingerprint`) counts as dirty: the tick prints RUN and writes a good file. Never hand-edit it; delete it to force
  one RUN on the next tick.
- The state file is written before the caller's work runs. A tick that RUNs and then fails would SKIP next time:
  delete the state file after a failed run.
- The state file must live outside the `--watch` dir. The script refuses a state path inside it: stdout
  `ERROR refused: ... inside the watch dir ...`, exit 2, nothing written.
- `ERROR watch dir missing: <dir>` (exit 2): the folder does not exist; no state file or folder is created.
- `ERROR cannot read <file>: <reason>; state untouched` (exit 2): a file in the folder is locked or unreadable, so no
  fingerprint can be made. Fix the file or stop the program that holds it, then tick again.
