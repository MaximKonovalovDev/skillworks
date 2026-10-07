# Sources and licences (read 2026-10-07)

The skill text and every example are written fresh. The octokit/request.js sources below were read to check each rule. Only short code tokens and output fragments are quoted, each with its file.

- octokit/request.js, commit 999fad9ce9ed4e9428c7e17da1795c80d1df52d6 on main (pushed 2026-10-05), read 2026-10-07 from a local download in `work/octokit-request/src/` (git-ignored, never committed). Upstream https://github.com/octokit/request.js, verified live 2026-10-07.
  - Licence: MIT (licence spdx read live 2026-10-07, LICENSE blob sha af5366d0d043f11684e13d78c048a33e80a58fe3). Permissive: no NonCommercial and no priced restriction, so this skill may be shared; attribution via the credit line below.
  - Files used: the two sources fetch-wrapper.ts (sha256 starts f70456d6f3a3bc72b65652a478cc531a7703551c61eb6e85f77bdb68167ae901) and with-defaults.ts (sha256 starts ca96e5923a141b57199f098162957f2ad156b490868d355eba75203d4b67c176).
  - Commands quoted in SKILL.md and cheatsheet.md were replayed on this PC with rg on 2026-10-07 (each ends exit 0), not copied from the docs.
- The trial sheet `evals/octokit-request_trials.jsonl` (12 tasks: 8 answer, 4 run) pins each task to its source section via its `locator` field at commit 999fad9c.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 trial rows above (`evals/octokit-request_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: octokit/request.js (MIT, pinned 999fad9c read 2026-10-07; own words and own examples, short quotes only).
