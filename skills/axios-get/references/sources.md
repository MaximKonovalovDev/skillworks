# Sources and licences (read 2026-10-07)

The skill text and every example are written fresh. The axios/axios sources below were read to check each rule. Only short code tokens and output fragments are quoted, each with its file.

- axios/axios, commit 2b169bbb0cf67e6539e4cec222ced5ac8a923e00 on v1.x (pushed 2026-10-06), read 2026-10-07 from a local download in `work/axios-get/src/` (git-ignored, never committed). Upstream https://github.com/axios/axios, verified live 2026-10-07.
  - Licence: MIT (licence spdx read live 2026-10-07, LICENSE blob sha 05006a51eb888282323883df740cd90ad72d0700). Permissive: no NonCommercial and no priced restriction, so this skill may be shared; attribution via the credit line below.
  - Files used: the two sources AxiosError.js (sha256 starts 6c2860a06292ab37) and CanceledError.js (sha256 starts 227a7f7d6b1f14d83560438e).
  - Commands quoted in SKILL.md and cheatsheet.md were replayed on this PC with rg on 2026-10-07 (each ends exit 0), not copied from the docs.
- The trial sheet `evals/axios-get_trials.jsonl` (12 tasks: 8 answer, 4 run) pins each task to its source section via its `locator` field at commit 2b169bbb.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 trial rows above (`evals/axios-get_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: axios/axios (MIT, pinned 2b169bbb read 2026-10-07; own words and own examples, short quotes only).
