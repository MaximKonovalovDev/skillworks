# Cost model

`pipe_run.py` estimates batch cost before writing anything.

## What is priced

- One item is one `.txt` file at the top level of `--input` (the suffix is matched in any letter case). A folder named
  like an item, a file in a subfolder, `.md`, `.txt.bak` and files without a suffix are not items.
- Items are read in sorted name order, so repeat runs over the same folder give the same lines and the same record file.
- One item's cost is `chars // 4`, at least 1. Characters of the UTF-8 text, not bytes. A line break (`\r\n`, `\n` or
  `\r`) counts as one character on every system. Batch spend is the sum over items. An empty folder costs 0.
- A file that is not UTF-8 text cannot be priced: `ERROR refused: <name> is not UTF-8 text; nothing written`, exit 2,
  for the dry run as well as the real run.

## The cap

- `--cap <tokens>` is a ceiling on the sum: spend equal to the cap runs, one more is refused. It must be a whole number
  of at least 0 (`ERROR cap must be >= 0, got <n>`, exit 2; text such as `ten` is an argparse usage error, exit 2).
- Over the cap the run is refused: exit 2, stdout `ERROR over cap: spend <S> tokens > cap <C> tokens, refused; nothing
  written`, and the `--out` folder is never created.

## The three modes

- `--dry-run` prints `DRY-RUN <n> items spend <S> tokens (cap <C>)`, exits 0 and writes nothing. It prints that line
  even when `S` is over `C`: compare the two numbers yourself.
- A run under the cap copies each item into `--out` byte for byte (line endings and a byte order mark are kept), writes
  `receipt.json` `{"tool": "pipe-run", "items": n, "spend": S, "cap": C}`, prints `RUN <n> items spend <S>/<C> tokens`
  and exits 0. A second run into the same `--out` overwrites the items and `receipt.json`.
- A refusal prints one `ERROR` line, exits 2 and writes nothing: `--input` is not a folder, `--out` is the input folder
  (`ERROR refused: --out is the input dir`), `--out` is an existing file (`ERROR refused: --out is a file`), a negative
  cap, or an item that cannot be read.

## Notes

- The estimate is the same unit as the audit token estimate of this repository (`chars // 4`). It is a planning number,
  not a model's exact count: leave headroom in the cap.
- `--out` may sit inside `--input` as a subfolder, because only top-level files are items. Giving the same folder for
  both is refused.
