# Sources and licences (read 2026-10-06)

The skill text and every example are written fresh. The docs below were read to check each rule. Only short command lines and output fragments are quoted, each with its file.

- microsoft/playwright docs, commit d0fd0f22ffad53804c0a326a692ee6b8e70ada3d on main (pushed 2026-10-05), read 2026-10-06 from a local download in `work/playwright-docs/src/` (git-ignored, never committed). Upstream https://github.com/microsoft/playwright, verified live 2026-10-06.
  - Licence: Apache-2.0 (LICENSE blob sha df112373eb2e23e459bf93ec412be1764dc5a38b, API record spdx Apache-2.0 re-read live 2026-10-06 via gh api). Permissive: no NonCommercial or ShareAlike restriction, so this skill may be shared and sold; attribution via the credit line below.
  - Files used: locators.md, actionability.md, navigations.md, best-practices-js.md, debug.md, auth.md, network.md, frames.md, pages.md, browser-contexts.md, intro-js.md.
  - Command outputs quoted in pairs.md were measured on this PC with gh 2.88.1 on 2026-10-06, not copied from the docs.
- The trial sheet `evals/playwright-docs_trials.jsonl` (12 tasks: 7 answer, 5 run) pins each task to its docs section via its `locator` field at commit d0fd0f22.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 tested pairs in `references/pairs.md` (each section carries a `prints:` line) plus the 12 trial rows above (`evals/playwright-docs_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: microsoft/playwright docs (Apache-2.0, pinned d0fd0f22 read 2026-10-06; own words and own examples, short quotes only).
