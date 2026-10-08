# Sources and licences (read 2026-10-08)

The skill text and every example are written fresh. The lsd-rs/lsd sources below were read to check each rule. Only short code tokens and output fragments are quoted, each with its file.

- lsd-rs/lsd, commit 4b6c14a110fe0fd544ec0204501b5fd3a5d6218f on main (read 2026-10-08 from a local download in `work/lsd-ls/src/`, git-ignored, never committed). Upstream https://github.com/lsd-rs/lsd, verified live 2026-10-08.
  - Licence: Apache License 2.0 (licence spdx read live 2026-10-08). Permissive: no NonCommercial and no priced restriction, so this skill may be shared; attribution via the credit line below.
  - Files used: the two sources README.md (sha256 starts 71014929) and lsd.md (sha256 starts c140e0c4).
  - Commands quoted in SKILL.md and cheatsheet.md were replayed on this PC with rg on 2026-10-08 (each ends exit 0), not copied from the docs.
  - eza-community/eza was rejected as a donor: its repo licence spdx is EUPL-1.2 read live 2026-10-08, so only lsd-rs/lsd wording is quoted.
- The trial sheet `evals/lsd-ls_trials.jsonl` (12 tasks: 8 answer, 4 run) pins each task to its source section via its `locator` field at commit 4b6c14a1.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 tested pairs in `references/pairs.md` plus the 12 trial rows above (`evals/lsd-ls_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: lsd-rs/lsd (Apache-2.0, pinned 4b6c14a1 read 2026-10-08; own words and own examples, short quotes only).
