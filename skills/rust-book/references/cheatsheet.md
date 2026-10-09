# Cheatsheet

Commands: `rustc --edition 2021 file.rs` compiles one file; failing programs exit 1 and print `error[EXXXX]` on stderr.

Codes: `E0382` moved value, fix `clone()` or borrow. `E0502` mixed borrows, end the `&` borrow first. `E0004` missing arm, add it or `_` last. `E0277` bad index or `?` in `()` main, use `get` or return `Result`.

Signatures: `fn first_word(s: &str) -> &str`. `fn longest<'a>(x: &'a str, y: &'a str) -> &'a str`. `fs::read_to_string(path)?` only inside a `Result` function. `fn main() -> Result<(), Box<dyn Error>>` allows `?` with `Ok(())` at the end.

Collections: `Vec::new()` or `vec![]`, `push` and `pop`. `&v[2]` panics past the end, `v.get(2)` gives `Option`. `String::from`, `push_str` and `push`, `+` moves left, `format!` borrows. `s[0]` never compiles, use `chars()` or `bytes()`. `HashMap::new()` with `use std::collections::HashMap`, `get` with `copied().unwrap_or(0)`, `entry(key).or_insert(v)` for check-then-insert.

Errors: `panic!` unwinds (or aborts), read `RUST_BACKTRACE=1` from the first own file. `expect` over `unwrap` in production. `ErrorKind::NotFound` creates, `_` panics. Return `Result` by default, panic on broken contracts.

Pointers: `Box<T>` single-owner recursion. `Rc<T>` plus `Rc::clone` many immutable owners, one thread. `Rc<RefCell<T>>` many mutable owners, runtime checks.

Rules: one owner; one `&mut` or many `&`; references always valid; `match` exhaustive; `?` needs a compatible return.
