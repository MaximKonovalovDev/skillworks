---
name: pipe-run
description: Price a batch of text files and refuse it before anything is written when it would spend more than a token cap, with a dry run to preview the spend. Use before a headless batch job over a folder of .txt items (a model run, a bulk rewrite, a scan) when an over-budget run must stop first; RUN under the cap, refuse over it, DRY-RUN to see the number.
version: 0.1.0
license: MIT
---

# pipe-run

Run a batch, or refuse it. Headless: no network, no prompts. It prices every `.txt` file at the top level of an input
folder at `chars // 4` tokens and runs only when the total fits the cap.

## Use it

Run `scripts/pipe_run.py` from this skill's folder, or give its full path:

```powershell
python scripts/pipe_run.py --input <dir> --out <dir> --cap <tokens> --dry-run
python scripts/pipe_run.py --input <dir> --out <dir> --cap <tokens>
```

Dry run first to see the number, then the real run. The first word of stdout is the answer:

- `DRY-RUN <n> items spend <S> tokens (cap <C>)`: exit 0, nothing written, even when the spend is over the cap.
- `RUN <n> items spend <S>/<C> tokens`: exit 0. Each item is copied byte for byte into `--out`, with a `receipt.json`
  of `{tool, items, spend, cap}`.
- `ERROR over cap: spend <S> tokens > cap <C> tokens, refused; nothing written`: exit 2, `--out` is never created.
- Other `ERROR ...` lines also exit 2 with nothing written: missing input folder, negative cap, `--out` is the input
  folder or a file, an item that is not UTF-8 text. A cap that is not a whole number is a usage error (exit 2).

## Rules

- A spend equal to the cap runs. One token more is refused.
- Only `.txt` files at the top level of `--input` are items, in any letter case, sorted by name. Subfolders, `.md` and
  other files are ignored and not priced.
- One item costs `chars // 4`, at least 1. Characters, not bytes: a Hebrew letter is one. A line break counts one.
- The batch is yours to run: this tool prices and copies, it does not call a model. Run your model step on the files in
  `--out` after `RUN`, and take `receipt.json` as the proof of what was priced.
- Same input and cap give the same output, so a repeat run is safe. A second `RUN` into the same `--out` overwrites.

Cost units, exit codes and the record file: `references/cost-model.md`.
