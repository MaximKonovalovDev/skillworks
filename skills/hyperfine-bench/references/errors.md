# Error lines the pairs replay (all thrown live by scripts/run_hyperfine.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the fixed-query report instead.

- `--warmup`: benchmarked cold with no warmup. Pair `hb-p01`
- `parameter-scan`: ran one thread count with no scan. Pair `hb-p02`
- `shell spawning time`: timed the shell with no mode branch. Pair `hb-p03`
- `OUTLIER_THRESHOLD`: kept every sample with no filter. Pair `hb-p04`
- `memory_peak_resident`: timed wall only with no metric choice. Pair `hb-p05`
- `Markdown`: kept results on screen with no export. Pair `hb-p06`
- `HYPERFINE_ITERATION`: used a fixed env with no per-run names. Pair `hb-p07`
- `LICENSE-APACHE`: shipped without clearing the licence. Pair `hb-p08`
- `missed warmup`: queried plain.txt for the warmup phrase. Pair `hb-p09`
- `missed OUTLIER_THRESHOLD`: queried plain.txt for the threshold phrase. Pair `hb-p10`
- `missed parameter-scan`: queried plain.txt for the scan phrase. Pair `hb-p11`
- `missed modified_zscores`: queried plain.txt for the zscore phrase. Pair `hb-p12`
