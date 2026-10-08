# Sources and licences (read 2026-10-08)

The skill text and every example are written fresh. The chmln/sd sources below were read to check each rule. Only short code tokens and output fragments are quoted, each with its file.

- chmln/sd, commit 44febdf86343c653255ae4f20f5e1882dad6be17 on master (read 2026-10-08 from a local download in `work/sd-replace/src/`, git-ignored, never committed). Upstream https://github.com/chmln/sd, verified live 2026-10-08.
  - Licence: MIT (licence spdx read live 2026-10-08). Permissive: no NonCommercial and no priced restriction, so this skill may be shared; attribution via the credit line below.
  - Files used: the two sources README.md (sha256 starts 9908fcf5) and input.rs (sha256 starts d050f790).
  - Commands quoted in SKILL.md and cheatsheet.md were replayed on this PC with rg on 2026-10-08 (each ends exit 0), not copied from the docs.
  - BurntSushi/ripgrep was rejected as a donor: its Unlicense scope covers search precision, not find plus replace preview, so only chmln/sd wording is quoted.
- The trial sheet `evals/sd-replace_trials.jsonl` (12 tasks: 8 answer, 4 run) pins each task to its source section via its `locator` field at commit 44febdf8.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 tested pairs in `references/pairs.md` plus the 12 trial rows above (`evals/sd-replace_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: chmln/sd (MIT, pinned 44febdf8 read 2026-10-08; own words and own examples, short quotes only).
