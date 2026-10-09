# Fix patterns per error code

Each pattern: symptom, the rule, the sanctioned fix, and how to confirm.

## E0382 borrow of moved value

Symptom: use of a `String` (or other non-`Copy` value) after `let s2 = s1;` or after passing it by value. Fix: clone at the move (`s1.clone()`), borrow instead of moving (`&s1`), or have the function take `&str`. Confirm: `rustc --edition 2021` compiles clean.

## E0502 cannot borrow as mutable

Symptom: `&mut s` created while an `&s` borrow is still used later. Fix: end the immutable borrow first by narrowing its scope, so the last use of `r1` comes before `let r2 = &mut s;`. Confirm: recompile; no `E0502`. Engine case: `&v[0]` held across `v.push(6)` fails the same way because growing may reallocate; drop the reference first, then push.

## E0004 non-exhaustive patterns

Symptom: `match` on `Option` (or another enum) missing a variant. Fix: add the missing arm explicitly (`None => ...`) or a trailing `_` catch-all. Confirm: recompile; the compiler names any still-missing pattern.

## ? operator in the wrong function

Symptom: `?` on a `Result` inside a function returning `()`, such as `fn main()`. Fix: change the function to return a compatible type (`Result<(), E>`) or replace `?` with match-and-return. Confirm: recompile; the `?` desugars to the match form in match-result.md.

## Missing lifetime on a returned reference

Symptom: the borrow checker cannot infer which input a returned `&str` follows. Fix: write one shared parameter as in `fn longest<'a>(x: &'a str, y: &'a str) -> &'a str`. Confirm: recompile; callers must keep both inputs alive.

## Choosing the smart pointer

Symptom: recursive type will not compile, or shared ownership will not type-check. Fix: single owner plus recursion gets `Box<T>`; several immutable owners on one thread get `Rc<T>` with `Rc::clone`; several mutable owners on one thread get `Rc<RefCell<T>>`. Confirm: `cargo build` (or `rustc`) passes and drops happen once.

## Index past the end of a Vec

Symptom: `&v[100]` on a 5-element vector panics at runtime (`index out of bounds`). Fix: use `v.get(100)` and match `Some` against `None` when the index may be wrong; keep `[]` only when the index must exist. Confirm: run the binary; wrong input prints the fallback instead of `thread 'main' panicked`.

## E0277 indexing into a String

Symptom: `s1[0]` refused because `str` cannot be indexed by integer. Fix: slice by ranges on character boundaries (`&hello[0..4]`), or iterate with `chars()` and `bytes()`. Confirm: recompile; a mid-character slice still panics at runtime, so keep slices on boundaries.

## HashMap insert versus entry

Symptom: repeated `insert` overwrites the stored value, or `insert` moves `String` keys and values. Fix: `entry(key).or_insert(v)` inserts only when absent; read with `get(&key).copied().unwrap_or(0)`; count with `*count += 1` on the returned `&mut V`. Confirm: run the binary; the word-count program prints `3 2`.

## panic versus Result

Symptom: unsure whether to stop or to return. Fix: return `Result` by default (examples, prototypes, and tests may panic with `unwrap` or `expect`); panic on broken contracts and bad states, branch `ErrorKind::NotFound` to create and `_` to panic, and prefer `expect` with context over `unwrap`. Confirm: `RUST_BACKTRACE=1` points at the first own file; callers of a `Result` function decide.
