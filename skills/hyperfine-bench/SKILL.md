---
name: hyperfine-bench
description: Use when benchmarking commands with hyperfine: warmup runs, parameter scans, shell modes, outlier filtering with modified Z-scores, metrics choice, CSV JSON Markdown exports, env setup, Apache-2.0 or MIT licence.
version: 0.1.0
author: skillworks
license: MIT
---

# Benchmark timing with hyperfine, the statistical runner

Rules distilled from sharkdp/hyperfine at `b33755fe` (master, read 2026-10-08) for the benchmark-timing class: what the runner measures, how warmup plus scans spell, how shell modes subtract startup, how outliers filter, which metrics export, and which licence covers the slice. Each rule names the exact token to branch on and the pair that replays it. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`. The runnable proof of every rule is `references/pairs.md` (machine list `references/pairs.json`), replayed by `scripts/run_hyperfine.py`.

## Warmup and scans

- hyperfine is a `benchmark` runner; for a warm cache use `warmup` with the `--warmup` flag like `--warmup 3` [src: references/pairs.md#hb-p01]
- Parameterized runs use `parameter-scan` with the `num_threads` variable and the `{num_threads}` placeholder [src: references/pairs.md#hb-p02]
- Default mode is `--shell=none` with no intermediate shell; `-S` enables shell syntax and hyperfine subtracts the `shell spawning time` [src: references/pairs.md#hb-p03]
- The cutoff `OUTLIER_THRESHOLD` equals `1.4826` times ten; points above it fail the `modified Z-score` test [src: references/pairs.md#hb-p04]

## Metrics and exports

- Default metrics are `time_wall_clock` plus `memory_peak_resident`; choose more with the `--metrics` comma list [src: references/pairs.md#hb-p05]
- Export results as `CSV` for scripts plus `JSON` for data plus `Markdown` for reports [src: references/pairs.md#hb-p06]
- Set per-run vars with `--env` like `OMP_NUM_THREADS` equals eight, and name logs with `HYPERFINE_ITERATION` [src: references/pairs.md#hb-p07]
- Offered under the `MIT License` plus the `Apache License 2.0` with the `LICENSE-APACHE` file [src: references/pairs.md#hb-p08]

## Paths and staged errors

- Line `56` of `README.md` shows `warmup` use: the token appears 5 times starting at lines `56` and `59` [src: references/pairs.md#hb-p09]
- Line `11` of `outlier_detection.rs` shows `OUTLIER_THRESHOLD` statics: the token appears 3 times starting at lines `11` and `14` [src: references/pairs.md#hb-p10]
- Line `77` of `README.md` shows `parameter-scan` use: the token appears 3 times starting at lines `77` and `79` [src: references/pairs.md#hb-p11]
- Line `17` of `outlier_detection.rs` shows `modified_zscores` use: the token appears 2 times starting at lines `17` and `23` [src: references/pairs.md#hb-p12]

## Prove the pin

Replayed live 2026-10-08 with the installed `rg` (each replay ends exit 0):

```
rg -n "warmup" work/hyperfine-bench/src/README.md
```

prints 5 match lines at lines `56`, `59`, `112`, `285` and `317` where line `56` opens the warmup option. `rg -n "OUTLIER_THRESHOLD" work/hyperfine-bench/src/outlier_detection.rs` prints 3 match lines at lines 11, `14` and `26`, where line `11` defines OUTLIER_THRESHOLD. `rg -n "parameter-scan" work/hyperfine-bench/src/README.md` prints 3 match lines at lines 77, `79` and `84`, where line `77` opens the scan option. `rg -n "modified_zscores" work/hyperfine-bench/src/outlier_detection.rs` prints 2 match lines at lines 17 and `23`, where line `17` imports modified_zscores_f64.
