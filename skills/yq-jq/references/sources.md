# Sources and licences (read 2026-10-07)

The skill text and every example are written fresh. The kislyuk/yq sources below were read to check each rule. Only short code tokens and output fragments are quoted, each with its file.

- kislyuk/yq, commit b04512f9bb1669b29c4e4443003bb8a2a7d3e59f on main (pushed 2026-09-27), read 2026-10-07 from a local download in `work/yq-jq/src/` (git-ignored, never committed). Upstream https://github.com/kislyuk/yq, verified live 2026-10-07.
  - Licence: Apache-2.0 (licence spdx read live 2026-10-07, LICENSE blob sha 37ec93a14fdcd0d6e525d97c0cfa6b314eaa98d8). Permissive: no NonCommercial and no priced restriction, so this skill may be shared; attribution via the credit line below.
  - Files used: the two sources __init__.py (sha256 starts e6f14d574cfd6536) and README.rst (sha256 starts 62d6526dc7a462b).
  - Commands quoted in SKILL.md and cheatsheet.md were replayed on this PC with rg on 2026-10-07 (each ends exit 0), not copied from the docs.
  - jqlang/jq was rejected as a donor: its repo licence spdx is NOASSERTION read live 2026-10-07, so only kislyuk/yq wording is quoted.
- The trial sheet `evals/yq-jq_trials.jsonl` (12 tasks: 8 answer, 4 run) pins each task to its source section via its `locator` field at commit b04512f9.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 tested pairs in `references/pairs.md` plus the 12 trial rows above (`evals/yq-jq_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: kislyuk/yq (Apache-2.0, pinned b04512f9 read 2026-10-07; own words and own examples, short quotes only).
