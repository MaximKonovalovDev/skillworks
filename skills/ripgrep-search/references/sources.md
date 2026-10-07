# Sources and licences (read 2026-10-07)

The skill text and every example are written fresh. The BurntSushi/ripgrep docs below were read to check each rule. Only short command lines and output fragments are quoted, each with its file.

- BurntSushi/ripgrep, commit 3fce3b5bb0236da2df6d99672afb8a719642eca7 on master (pushed 2026-08-04), read 2026-10-07 from a local download in `work/ripgrep-search/src/` (git-ignored, never committed). Upstream https://github.com/BurntSushi/ripgrep, verified live 2026-10-07.
  - Licence: dual Unlicense plus MIT (UNLICENSE blob sha 7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c on disk; FAQ section "How is ripgrep licensed" offers either licence, re-read live 2026-10-07). Permissive: no NonCommercial and no ShareAlike restriction, so this skill may be shared and sold; attribution via the credit line below.
  - Files used: GUIDE.md (sha256 starts 156337b59d9813b), FAQ.md (sha256 starts 4359aaf42d65b787), UNLICENSE (sha256 starts 7e12e5df4bae12c).
  - Commands quoted in patterns.md and cheatsheet.md were replayed on this PC with rg on 2026-10-07 (each ends exit 0), not copied from the docs.
- The trial sheet `evals/ripgrep-search_trials.jsonl` (12 tasks: 8 answer, 4 run) pins each task to its docs section via its `locator` field at commit 3fce3b5b.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 trial rows above (`evals/ripgrep-search_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: BurntSushi/ripgrep (Unlicense OR MIT, pinned 3fce3b5b read 2026-10-07; own words and own examples, short quotes only).
