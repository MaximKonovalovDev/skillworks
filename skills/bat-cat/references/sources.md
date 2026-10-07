# Sources and licences (read 2026-10-07)

The skill text and every example are written fresh. The sharkdp/bat sources below were read to check each rule. Only short code tokens and output fragments are quoted, each with its file.

- sharkdp/bat, commit d9559c69f541873f8c47ac8ad81d985f4441edf6 on master (read 2026-10-07 from a local download in `work/bat-cat/src/`, git-ignored, never committed). Upstream https://github.com/sharkdp/bat, verified live 2026-10-07.
  - Licence: Apache-2.0 (licence spdx read live 2026-10-07). Permissive: no NonCommercial and no priced restriction, so this skill may be shared; attribution via the credit line below.
  - Files used: the two sources README.md (sha256 starts df367a) and pager.rs (sha256 starts fbcee7).
  - Commands quoted in SKILL.md and cheatsheet.md were replayed on this PC with rg on 2026-10-07 (each ends exit 0), not copied from the docs.
  - jqlang/jq was rejected as a donor: its repo licence spdx is NOASSERTION read live 2026-10-07, so only sharkdp/bat wording is quoted.
- The trial sheet `evals/bat-cat_trials.jsonl` (12 tasks: 8 answer, 4 run) pins each task to its source section via its `locator` field at commit d9559c69.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 tested pairs in `references/pairs.md` plus the 12 trial rows above (`evals/bat-cat_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: sharkdp/bat (Apache-2.0, pinned d9559c69 read 2026-10-07; own words and own examples, short quotes only).
