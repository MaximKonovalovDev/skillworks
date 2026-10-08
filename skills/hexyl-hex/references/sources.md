# Sources and licences (read 2026-10-08)

The skill text and every example are written fresh. The sharkdp/hexyl sources below were read to check each rule. Only short code tokens and output fragments are quoted, each with its file.

- sharkdp/hexyl, commit 6ecc29b9c8c84d08a7e860f7f69c22b113b480ea on master (read 2026-10-08 from a local download in `work/hexyl-hex/src/`, git-ignored, never committed). Upstream https://github.com/sharkdp/hexyl, verified live 2026-10-08.
  - Licence: Apache-2.0 plus MIT at your option (licence spdx read live 2026-10-08). Permissive: no NonCommercial and no priced restriction, so this skill may be shared; attribution via the credit line below.
  - Files used: the two sources README.md (sha256 starts 6ccc241d) and colors.rs (sha256 starts 27df8760).
  - Commands quoted in SKILL.md and cheatsheet.md were replayed on this PC with rg on 2026-10-08 (each ends exit 0), not copied from the docs.
  - sharkdp/bat was rejected as a donor: its Apache-2.0 scope covers paged cat reading with pager precedence, not binary hex viewing with byte categories, so only sharkdp/hexyl wording is quoted.
- The trial sheet `evals/hexyl-hex_trials.jsonl` (12 tasks: 8 answer, 4 run) pins each task to its source section via its `locator` field at commit 6ecc29b9.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 tested pairs in `references/pairs.md` plus the 12 trial rows above (`evals/hexyl-hex_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: sharkdp/hexyl (Apache-2.0 plus MIT, pinned 6ecc29b9 read 2026-10-08; own words and own examples, short quotes only).
