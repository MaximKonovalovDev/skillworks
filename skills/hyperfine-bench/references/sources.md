# Sources and licences (read 2026-10-08)

The skill text and every example are written fresh. The sharkdp/hyperfine sources below were read to check each rule. Only short code tokens and output fragments are quoted, each with its file.

- sharkdp/hyperfine, commit b33755fe1fca8bcc1f182c773ca3ab040bfe517d on master (read 2026-10-08 from a local download in `work/hyperfine-bench/src/`, git-ignored, never committed). Upstream https://github.com/sharkdp/hyperfine, verified live 2026-10-08.
  - Licence: MIT License plus Apache License 2.0 at your option (licence spdx read live 2026-10-08). Permissive: no NonCommercial and no priced restriction, so this skill may be shared; attribution via the credit line below.
  - Files used: the two sources README.md (sha256 starts 03e31b51) and outlier_detection.rs (sha256 starts c1fe017f).
  - Commands quoted in SKILL.md and cheatsheet.md were replayed on this PC with rg on 2026-10-08 (each ends exit 0), not copied from the docs.
  - sharkdp/bat was rejected as a donor: its Apache-2.0 scope covers paged cat reading with pager precedence, not statistical benchmarking with warmup plus scans plus outliers, so only sharkdp/hyperfine wording is quoted.
- The trial sheet `evals/hyperfine-bench_trials.jsonl` (12 tasks: 8 answer, 4 run) pins each task to its source section via its `locator` field at commit b33755fe.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 tested pairs in `references/pairs.md` plus the 12 trial rows above (`evals/hyperfine-bench_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: sharkdp/hyperfine (MIT plus Apache-2.0, pinned b33755fe read 2026-10-08; own words and own examples, short quotes only).
