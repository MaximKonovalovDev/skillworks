# Sources and licences (read 2026-10-07)

The skill text and every example are written fresh. The sharkdp/fd docs below were read to check each rule. Only short command lines and output fragments are quoted, each with its file.

- sharkdp/fd, commit 14dcd92fb76ca0ebc2e82671a275f67c790d25fc on master (pushed 2026-10-06), read 2026-10-07 from a local download in `work/fd-find/src/` (git-ignored, never committed). Upstream https://github.com/sharkdp/fd, verified live 2026-10-07.
  - Licence: Apache-2.0 (spdx read live 2026-10-07 per board BK-1007-4; LICENSE-APACHE blob on disk). Permissive: no NonCommercial and no ShareAlike restriction, so this skill may be shared and sold; attribution via the credit line below.
  - Files used: README.md (603 lines), fd.1 (588 lines) at the pinned commit.
  - Commands quoted in patterns.md and cheatsheet.md were checked against this PC with rg on 2026-10-07 (each ends exit 0), not copied from the docs.
- The trial sheet `evals/fd-find_trials.jsonl` (12 tasks: 8 answer ff-a01 to ff-a08, 4 run ff-r01 to ff-r04) pins each task to its docs section via its `locator` field at commit 14dcd92f.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 trial rows above (`evals/fd-find_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: sharkdp/fd (Apache-2.0, pinned 14dcd92f read 2026-10-07; own words and own examples, short quotes only).
