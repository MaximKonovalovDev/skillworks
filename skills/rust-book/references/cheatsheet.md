# Cheatsheet

Commands: `rustc --edition 2021 file.rs` compiles one file; failing programs exit 1 and print `error[EXXXX]` on stderr.

Codes: `E0382` moved value, fix `clone()` or borrow. `E0502` mixed borrows, end the `&` borrow first. `E0004` missing arm, add it or `_` last.

Signatures: `fn first_word(s: &str) -> &str`. `fn longest<'a>(x: &'a str, y: &'a str) -> &'a str`. `fs::read_to_string(path)?` only inside a `Result` function.

Pointers: `Box<T>` single-owner recursion. `Rc<T>` plus `Rc::clone` many immutable owners, one thread. `Rc<RefCell<T>>` many mutable owners, runtime checks.

Rules: one owner; one `&mut` or many `&`; references always valid; `match` exhaustive; `?` needs a compatible return.
