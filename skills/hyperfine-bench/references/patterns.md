# Patterns: symptom to branch

Each recipe starts from a benchmark-timing miss the loop really makes, then names the one branch that fixes it. All replays ran on this PC on 2026-10-08.

## Cold cache noise

Symptom: the loop benchmarks on a cold disk cache and gets noise.

- hyperfine is a `benchmark` runner; for a warm cache use `warmup` with `--warmup 3` (pair `hb-p01`).
- prints: `warm PASS warm-cache`

## One thread count

Symptom: the loop runs one thread count and cannot compare scaling.

- Parameterized runs use `parameter-scan` with `num_threads` and the `{num_threads}` placeholder (pair `hb-p02`).
- prints: `param PASS param-scan`

## Shell overhead timing

Symptom: a fast command measures the shell instead of itself.

- Default mode is `--shell=none`; `-S` enables shell syntax and hyperfine subtracts the `shell spawning time` (pair `hb-p03`).
- prints: `shell PASS shell-mode`

## Polluted samples kept

Symptom: other programs pollute timings and every sample is kept.

- The cutoff `OUTLIER_THRESHOLD` equals `1.4826` times ten for the `modified Z-score` test (pair `hb-p04`).
- prints: `out PASS outlier-rule`

## Wall time only

Symptom: wall time alone hides a memory regression.

- Default metrics are `time_wall_clock` plus `memory_peak_resident`; choose more with `--metrics` (pair `hb-p05`).
- prints: `met PASS metrics-choice`

## Results on screen

Symptom: the loop keeps results on screen and cannot script the report.

- Export results as `CSV` for scripts plus `JSON` for data plus `Markdown` for reports (pair `hb-p06`).
- prints: `exp PASS export-formats`

## Fixed environment

Symptom: the benchmark needs thread counts via the environment plus per-run logs.

- Set per-run vars with `--env` like `OMP_NUM_THREADS` and name logs with `HYPERFINE_ITERATION` (pair `hb-p07`).
- prints: `env PASS env-vars`

## Licence guess

Symptom: the loop ships the slice without clearing the licence.

- Offered under the `MIT License` plus the `Apache License 2.0` with the `LICENSE-APACHE` file (pair `hb-p08`).
- prints: `lic PASS dual-licence`
