# Sources and licences (read 2026-10-08)

The skill text and every example are written fresh. The sharkdp/vivid sources below were read to check each rule. Only short code tokens and output fragments are quoted, each with its file.

- sharkdp/vivid, commit 6f33cf1bcd4d6ee4465b1bc79a32ecaab3bed09a on master (read 2026-10-08 from a local download in `work/vivid-colors/src/`, git-ignored, never committed). Upstream https://github.com/sharkdp/vivid, verified live 2026-10-08.
  - Licence: Apache License 2.0 (licence spdx read live 2026-10-08). Permissive: no NonCommercial and no priced restriction, so this skill may be shared; attribution via the credit line below.
  - Files used: the two sources README.md (sha256 starts f571b5a8) and molokai.yml (sha256 starts a0dd172d).
  - Commands quoted in SKILL.md and cheatsheet.md were replayed on this PC with rg on 2026-10-08 (each ends exit 0), not copied from the docs.
- The trial sheet `evals/vivid-colors_trials.jsonl` (12 tasks: 8 answer, 4 run) pins each task to its source section via its `locator` field at commit 6f33cf1b.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 tested pairs in `references/pairs.md` plus the 12 trial rows above (`evals/vivid-colors_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: sharkdp/vivid (Apache-2.0, pinned 6f33cf1b read 2026-10-08; own words and own examples, short quotes only).
