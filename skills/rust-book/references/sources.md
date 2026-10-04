# Sources and licences (read 2026-10-04)

The skill text and every example are written fresh. The chapters below were read to check each rule. Only short error lines and the sanctioned signatures are quoted, each with its chapter.

- The Rust Programming Language (the Rust book), rust-lang/book, commit 1500248d8f230566e4ec9f27fcbb8fe9e2898ab1 on main (pushed 2026-09-02), read 2026-10-04 from a local download in `work/rust-book/src/` (git-ignored, never committed).
  - Licence: MIT OR Apache-2.0 (LICENSE-MIT and LICENSE-APACHE in the repo root; API record carries no single SPDX). Permissive: no NonCommercial or ShareAlike restriction, attribution via the credit line below.
  - Chapters used: ch04-01-what-is-ownership.md, ch04-02-references-and-borrowing.md, ch04-03-slices.md, ch06-02-match.md, ch09-02-recoverable-errors-with-result.md, ch10-03-lifetime-syntax.md, ch15-01-box.md, ch15-04-rc.md, ch15-05-interior-mutability.md.
  - Compiler outputs quoted in ownership.md, borrowing.md, and match-result.md were measured on this PC with rustc 1.97.1 on 2026-10-04, not copied from the book.
- The trial sheet `evals/rust-book_trials.jsonl` (12 tasks) pins each task to its chapter section via its `locator` field at commit 1500248d.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 trial rows above (`evals/rust-book_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: rust-book (MIT OR Apache-2.0 Rust book, rust-lang/book pinned 1500248d read 2026-10-04; own words and own examples, short quotes only).
