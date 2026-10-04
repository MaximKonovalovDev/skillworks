# Fix patterns per error code

Each pattern: symptom, the rule, the sanctioned fix, and how to confirm.

## E0382 borrow of moved value

Symptom: use of a `String` (or other non-`Copy` value) after `let s2 = s1;` or after passing it by value. Fix: clone at the move (`s1.clone()`), borrow instead of moving (`&s1`), or have the function take `&str`. Confirm: `rustc --edition 2021` compiles clean.

## E0502 cannot borrow as mutable

Symptom: `&mut s` created while an `&s` borrow is still used later. Fix: end the immutable borrow first by narrowing its scope, so the last use of `r1` comes before `let r2 = &mut s;`. Confirm: recompile; no `E0502`.

## E0004 non-exhaustive patterns

Symptom: `match` on `Option` (or another enum) missing a variant. Fix: add the missing arm explicitly (`None => ...`) or a trailing `_` catch-all. Confirm: recompile; the compiler names any still-missing pattern.

## ? operator in the wrong function

Symptom: `?` on a `Result` inside a function returning `()`, such as `fn main()`. Fix: change the function to return a compatible type (`Result<(), E>`) or replace `?` with match-and-return. Confirm: recompile; the `?` desugars to the match form in match-result.md.

## Missing lifetime on a returned reference

Symptom: the borrow checker cannot infer which input a returned `&str` follows. Fix: write one shared parameter as in `fn longest<'a>(x: &'a str, y: &'a str) -> &'a str`. Confirm: recompile; callers must keep both inputs alive.

## Choosing the smart pointer

Symptom: recursive type will not compile, or shared ownership will not type-check. Fix: single owner plus recursion gets `Box<T>`; several immutable owners on one thread get `Rc<T>` with `Rc::clone`; several mutable owners on one thread get `Rc<RefCell<T>>`. Confirm: `cargo build` (or `rustc`) passes and drops happen once.
