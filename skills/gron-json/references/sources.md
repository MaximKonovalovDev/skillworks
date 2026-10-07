# Sources and licences (read 2026-10-07)

The skill text and every example are written fresh. The tomnomnom/gron sources below were read to check each rule. Only short code tokens and output fragments are quoted, each with its file.

- tomnomnom/gron, commit 88a6234ea2d0c487090988182ad9a7cdf6def924 on main (read 2026-10-07 from a local download in `work/gron-json/src/`, git-ignored, never committed). Upstream https://github.com/tomnomnom/gron, verified live 2026-10-07.
  - Licence: MIT (licence spdx read live 2026-10-07). Permissive: no NonCommercial and no priced restriction, so this skill may be shared; attribution via the credit line below.
  - Files used: the two sources README.mkd (sha256 starts 8015dc) and statements.go (sha256 starts c9c98b).
  - Commands quoted in SKILL.md and cheatsheet.md were replayed on this PC with rg on 2026-10-07 (each ends exit 0), not copied from the docs.
  - stedolan/jq was rejected as a donor: its repo licence spdx is NOASSERTION read live 2026-10-07, so only tomnomnom/gron wording is quoted.
- The trial sheet `evals/gron-json_trials.jsonl` (12 tasks: 8 answer, 4 run) pins each task to its source section via its `locator` field at commit 88a6234e.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 tested pairs in `references/pairs.md` plus the 12 trial rows above (`evals/gron-json_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: tomnomnom/gron (MIT, pinned 88a6234e read 2026-10-07; own words and own examples, short quotes only).
