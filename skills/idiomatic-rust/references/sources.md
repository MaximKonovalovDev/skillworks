# Sources and licences (verified 2026-10-09)

The skill text and every example are written fresh. The book below was read to check each rule. Only short single-token names and output fragments are quoted, each with its section.

- Brenden Matthews, Idiomatic Rust: Code like a Rustacean, Manning 2024, ISBN 9781633437463. Upstream https://www.manning.com/books/idiomatic-rust, code companion https://github.com/brndnmtthws/idiomatic-rust-book, verified live 2026-10-09.
  - Licence: commercial, All rights reserved, read from an owned copy in `work/b1-idiomatic/` (git-ignored, never committed). Permissive reuse is limited to short tokens, so this skill quotes only single words like Builder, Newtype, RAII, Cow, Deref, UPPERCASE, CamelCase, snake_case, unwrap, blanket, prelude, singleton, unsafe.
  - Sections used: Part 1 Building blocks (Rust-y patterns, basic blocks, code flow), Part 2 Core Patterns (intro patterns, design patterns, designing a library), Part 3 Advanced Patterns (traits generics structs, state machines coroutines macros preludes), Part 4 Problem Avoidance (immutability, antipatterns with unwrap clones Deref singletons unsafe).
  - Snippets quoted in SKILL.md, patterns.md and pairs.md were written fresh on this PC with python 3.13 on 2026-10-09, not copied from the book.
- The trial sheet `evals/idiomatic-rust_trials.jsonl` (12 tasks) pins each task to its book part via its `locator` field at ISBN 9781633437463.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 tested pairs in `references/pairs.md` plus the 12 trial rows above (`evals/idiomatic-rust_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: idiomatic-rust (Manning Idiomatic Rust, ISBN 9781633437463 read 2026-10-09 from owned copy; own words and own examples, short tokens only; skill MIT).

