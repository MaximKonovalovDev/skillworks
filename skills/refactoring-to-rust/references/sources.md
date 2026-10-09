# Sources and licences (read 2026-10-09)

The skill text and every example are written fresh. The book below was read
to check each rule. Only short API names and command lines are quoted, each
with its chapter. No book text is copied.

- Mara L., Holmes J., Refactoring to Rust (Manning, 2025); Russian
  translation Perekhod na Rust (2025). Source: https://www.manning.com/books/refactoring-to-rust
  Verified 2026-10-09: the Manning catalogue page lists the title and the
  authors. Read 2026-10-09 from a local PDF in `work/b1-transition/`
  (git-ignored, never committed): 726674 chars, 346 pages, classic extract.
  - Licence: All rights reserved. Ideas only, no text copied: the port
    patterns (C strings via CString and CStr, extern C plus unsafe wrapped in
    a safe function, moves with clone, Result with the ? operator, Python
    classes via PyO3 pyclass, JS promises via wasm-bindgen, JSON via
    serde_json, web builds via wasm-pack) are standard Rust practice restated
    in our own words and examples.
  - Chapters used: ch.1 why Rust, ch.2 first port, ch.3 ownership and moves,
    ch.4 C interop and FFI, ch.5 safe wrappers, ch.6 Python and PyO3,
    ch.7 errors with Result, ch.8 Python to Rust case study, ch.9 WASM and JS,
    ch.10 WASM build and ship.
- The trial sheet `evals/refactoring-to-rust_trials.jsonl` (12 tasks) pins
  each task to its chapter above via its `locator` field.

This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk
refs are used; every SKILL.md rule is covered by the 12 trial rows above
(`evals/refactoring-to-rust_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: refactoring-to-rust (All rights
reserved book, ideas only, own words and own examples, short API names only).

