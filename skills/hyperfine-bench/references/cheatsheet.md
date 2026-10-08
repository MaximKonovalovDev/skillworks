# Cheatsheet: hyperfine-bench timing runs

One page. Every line replayed from the sharkdp/hyperfine sources at `b33755fe`.

## Warmup and scans

| See | Branch |
|---|---|
| noisy cold cache | `benchmark`, `warmup`, `--warmup` |
| vary the threads | `parameter-scan`, `num_threads`, `{num_threads}` |
| shell overhead | `--shell=none`, `-S`, `shell spawning time` |
| polluted samples | `OUTLIER_THRESHOLD`, `1.4826`, `modified Z-score` |

## Metrics and exports

| Want | Type |
|---|---|
| choose metrics | `time_wall_clock`, `memory_peak_resident`, `--metrics` |
| ship the report | `CSV`, `JSON`, `Markdown` |
| set the env | `--env`, `OMP_NUM_THREADS`, `HYPERFINE_ITERATION` |
| clear the slice | `MIT License`, `Apache License 2.0`, `LICENSE-APACHE` |

## Lines

| Want | Type |
|---|---|
| warmup claim | `warmup` 5 lines, first at line `56` with the warmup option |
| threshold claim | `OUTLIER_THRESHOLD` 3 lines, first at line `11` with the constant |
| scan claim | `parameter-scan` 3 lines, first at line `77` with the scan option |
| zscore claim | `modified_zscores` 2 lines, first at line `17` with the helper |

## Prove the pin

| Replay | Prints |
|---|---|
| `rg -n "warmup" work/hyperfine-bench/src/README.md` | 5 match lines, first at line `56` with warmup |
| `rg -n "OUTLIER_THRESHOLD" work/hyperfine-bench/src/outlier_detection.rs` | 3 match lines, first at line `11` with the threshold |
| `rg -n "parameter-scan" work/hyperfine-bench/src/README.md` | 3 match lines, first at line `77` with the scan |
| `rg -n "modified_zscores" work/hyperfine-bench/src/outlier_detection.rs` | 2 match lines, first at line `17` with the helper |
