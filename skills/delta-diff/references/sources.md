# Sources and licences (read 2026-10-07)

The skill text and every example are written fresh. The dandavison/delta sources below were read to check each rule. Only short code tokens and output fragments are quoted, each with its file.

- dandavison/delta, commit 3c2269c6b845913965575f11b0196d70ef5352f3 on main (read 2026-10-07 from a local download in `work/delta-diff/src/`, git-ignored, never committed). Upstream https://github.com/dandavison/delta, verified live 2026-10-07.
  - Licence: MIT (licence spdx read live 2026-10-07). Permissive: no NonCommercial and no priced restriction, so this skill may be shared; attribution via the credit line below.
  - Files used: the two sources README.md (sha256 starts 192dca) and side_by_side.rs (sha256 starts 79eb6c).
  - Commands quoted in SKILL.md and cheatsheet.md were replayed on this PC with rg on 2026-10-07 (each ends exit 0), not copied from the docs.
  - kislyuk/yq was rejected as a donor: its Apache-2.0 scope covers YAML transcode, not diff layout, so only dandavison/delta wording is quoted.
- The trial sheet `evals/delta-diff_trials.jsonl` (12 tasks: 8 answer, 4 run) pins each task to its source section via its `locator` field at commit 3c2269c6.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 tested pairs in `references/pairs.md` plus the 12 trial rows above (`evals/delta-diff_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: dandavison/delta (MIT, pinned 3c2269c6 read 2026-10-07; own words and own examples, short quotes only).
