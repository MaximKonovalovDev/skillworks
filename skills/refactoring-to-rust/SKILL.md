---
name: refactoring-to-rust
description: Other-language to Rust port patterns for stealing game code into Rust. Use when porting C, Python or JS game code to Rust or stealing Bevy methods into our renderer.
license: MIT
---

# refactoring-to-rust

Port other-language game code to Rust without guessing. Headless: no network, no prompts. Give it a snippet list and it names the Rust pattern for each line, so a steal lands in our renderer on the first try.

## Use it

Run `scripts/refactoring_to_rust.py` from this skill folder, or give its full path:

```powershell
python scripts/refactoring_to_rust.py --input <path> --out <path>
```

Start every call with `python scripts/refactoring_to_rust.py --input <path> --out <path>`.

The input file holds one snippet per line, each starting with a language tag (`C:`, `CPP:`, `PYTHON:`, `JS:`). The first word of stdout is the answer:

- `PORTED <p> patterns from <n> snippets to <out>`: exit 0. The report is written to `--out`, one `NN: <PATTERN> <= <snippet>` line per snippet.
- `ERROR missing input <path>`: exit 2, nothing written. The input file does not exist.
- `ERROR empty input <path>`: exit 2, nothing written. The input file holds no snippet lines.

## Rules

- A C string (`char*` with a null terminator) becomes `CString::new` on the way in and `CStr::from_ptr` on the way out; never move a Rust `String` across the boundary by value.
- The foreign boundary is always `extern "C"` on the Rust side with the call inside `unsafe`; wrap it the same day in a safe function so callers never write `unsafe` themselves.
- C++ copy semantics become an explicit move: write `let b = a;` and then either `a.clone()` or borrow with `&a`; use after move is error `E0382`.
- Fallible C or Python code becomes `Result<T, E>` with `?` on the happy path; a function using `?` must return `Result` or `Option`.
- A Python class becomes a `struct` plus an `impl` block; on the PyO3 boundary mark it with `#[pyclass]` and expose methods with `#[pymethods]`.
- A JS promise becomes an `async fn` behind `wasm-bindgen`; JSON crossing the boundary goes through `serde_json::from_str` with `serde-wasm-bindgen` types.
- Build the web target with `wasm-pack build` after `cargo install wasm-pack`; ship the `pkg` folder it writes, never hand-copied glue.
- Lines with no known marker map to `OTHER` and are still counted; the tool never refuses a line it can read.

Patterns, error codes and the WASM chain: `references/patterns.md`.

