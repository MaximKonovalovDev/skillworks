---
name: pipe-run
description: One-file batch pipeline with a cost cap and dry-run. Use for headless repeatable batch runs over a dir of text items when an over-budget run must be refused before it writes anything; RUN under cap, refuse over cap, DRY-RUN to preview spend.
---

# pipe-run

Run a batch, or refuse it. Headless: no phone, no network, no
prompts. Prices every `*.txt` item in an input dir at `chars // 4`
tokens, then runs only when the spend fits the cap.

## Use it

```powershell
python skills/pipe-run/scripts/pipe_run.py --input <dir> --out <dir> --cap <tokens>
python skills/pipe-run/scripts/pipe_run.py --input <dir> --out <dir> --cap <tokens> --dry-run
```

- Under cap: prints `RUN <n> items spend <S>/<C> tokens`, copies items
  to `--out` with a `receipt.json`.
- Over cap: prints `ERROR over cap: spend <S> tokens > cap <C> tokens,
  refused; nothing written`, exit 2, `--out` never created.
- Dry run: prints `DRY-RUN <n> items spend <S> tokens (cap <C>)`,
  exit 0, changes nothing.

Keep `--out` outside `--input`. Cost units and exit codes live in
`references/cost-model.md`.
