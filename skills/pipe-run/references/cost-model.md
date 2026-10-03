# Cost model

`pipe_run.py` estimates batch cost before writing anything.

- One item = one `*.txt` file in `--input`, read in sorted name order,
  so repeat runs over the same dir are byte-identical.
- One item's cost = `chars // 4` (minimum 1), the same unit as the
  audit token estimate. Batch spend = the sum over items.
- `--cap <tokens>` is the hard ceiling. When spend exceeds the cap the
  run is refused: exit code 2, stdout quotes the spend
  (`ERROR over cap: spend <S> tokens > cap <C> tokens, refused;
  nothing written`), and the `--out` dir is never created.
- `--dry-run` prints `DRY-RUN <n> items spend <S> tokens (cap <C>)`,
  exits 0, and writes nothing — safe to probe a batch before spending.
- A run under the cap copies items to `--out`, writes
  `receipt.json` `{tool, items, spend, cap}`, prints
  `RUN <n> items spend <S>/<C> tokens`, and exits 0.
- Keep `--out` outside `--input`, otherwise reruns would price their
  own outputs on the next batch.
