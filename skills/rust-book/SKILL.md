---
name: rust-book
description: Use when fixing a Rust borrow-checker or ownership rejection (moved value, mutable plus immutable borrow clash, non-exhaustive match, missing lifetime, ? in the wrong function), when choosing Vec, String, or HashMap for engine lists and maps, or when choosing panic versus Result: exact error codes, the book-sanctioned fix, and the signatures to write.
version: 1.1.0
author: skillworks
license: MIT
---

# Rust ownership and borrow-checker fixes

Fix-first rules distilled from the Rust book chapters on ownership, borrowing, slices, match, Result, panic, lifetimes, smart pointers, and collections (Vec, String, HashMap) for engine quality. Each rule names the exact compiler code and the sanctioned fix. Longer notes live in `references/`: per-group facts, `collections.md`, `errors.md`, `glossary.md`, `patterns.md`, and `cheatsheet.md`.

## Ownership and move

- A `String` moved with `let s2 = s1;` cannot be used as `s1` again; the compiler rejects it with `E0382` (`borrow of moved value`), so fix it with `s1.clone()` or borrow with `&s1` instead of moving [src: ch04-01-what-is-ownership.md]
- Every value has exactly one `owner` at a time and is `dropped` when the owner goes out of scope; `Copy` types like `i32` copy on assignment while `String` moves [src: ch04-01-what-is-ownership.md]

## Borrowing

- At any time hold either one `&mut s` mutable reference or any number of `&s` immutable references, never both; mixing them is rejected with `E0502` (`cannot borrow as mutable`), so end the immutable borrow (close its scope) before the mutable one [src: ch04-02-references-and-borrowing.md]
- Never return a `&` reference to a value created inside the function (a `dangling` reference); return an owned `String` or take the input by reference with a lifetime instead [src: ch04-02-references-and-borrowing.md]

## Slices, match, and Result

- Write string-taking functions as `fn first_word(s: &str) -> &str` rather than `&String`; the `&str` form accepts both `String` slices and string literals via `deref coercion` [src: ch04-03-slices.md]
- Every `match` must be exhaustive: matching `Some(v)` on `Option<i32>` without `None` fails with `E0004` (`non-exhaustive patterns`), so add the missing arm or a `_` catch-all arm last [src: ch06-02-match.md]
- Propagate errors with `fs::read_to_string(path)?` returning `Result<String, io::Error>`; the `?` operator is allowed only in functions whose return type (`Result` or `Option`) is compatible with the value it unwraps [src: ch09-02-recoverable-errors-with-result.md]

## Collections for engine lists and maps

- Build lists with `Vec::new()` (annotate the type when empty) or `vec![1, 2, 3]` (infers the type); grow with `push` and remove the last element with `pop` [src: ch08-storing-lists-with-vectors.md]
- Read an element with `&v[2]` (a reference) or `v.get(2)` (an `Option<&T>` matched with `Some` and `None`); indexing past the end with `[]` makes the program panic (`index out of bounds`) while `get` returns `None` [src: ch08-storing-lists-with-vectors.md]
- Never `push` while a reference such as `&v[0]` is still used later: growing may reallocate and leave a dangling pointer, so the checker rejects it with `E0502`; iterate with `for i in &v` (shared) or `for i in &mut v` with `*i +=` (exclusive), never insert or remove inside the loop, and know dropping the vector drops its elements [src: ch08-storing-lists-with-vectors.md]
- Grow text with `String::new()`, `to_string()`, or `String::from`; append a slice with `push_str` (takes `&str`, so the argument stays usable) and one character with `push`; join with `+` (moves the left side through `add(self, s: &str)` with `&String` to `&str` coercion) or with `format!` (borrows, clearer for many parts) [src: ch08-storing-utf8-text-with-strings.md]
- Never index a `String` (`s1[0]` fails with `E0277`); lengths count bytes, so slice by ranges (`&hello[0..4]`) only on character boundaries (a mid-character slice panics), iterate with `chars()` for scalar values or `bytes()` for raw `u8`, and search or substitute with `contains` and `replace` [src: ch08-storing-utf8-text-with-strings.md]
- Map keys to values with `HashMap::new()` plus `use std::collections::HashMap` (not in the prelude); read with `get(&key).copied().unwrap_or(0)` (an `Option<&V>`), iterate with `for (key, value) in &scores` in arbitrary order; `insert` moves owned `String` keys and values (unusable after) and overwrites the old value, while `entry(key).or_insert(50)` inserts only when absent and returns `&mut V` for word counts (`*count += 1` after dereference) [src: ch08-storing-keys-with-hash-maps.md]

## Panic versus Result

- Unrecoverable failures stop the program with `panic!` (prints `thread 'main' panicked`, unwinds and cleans the stack by default, or aborts with `panic = 'abort'`); read the location line, set `RUST_BACKTRACE=1` for the backtrace, and start from the first file the team wrote; indexing `v[99]` on a 3-element vector panics (`index out of bounds: the len is 3 but the index is 99`) [src: ch09-unrecoverable-errors-with-panic.md]
- Match `Result` arms `Ok` and `Err` directly, branch a missing file with `error.kind()` against `ErrorKind::NotFound` (create the file) versus `_` (panic), and prefer `expect` (own message) over `unwrap` (default message) in production code [src: ch09-recoverable-errors-with-result.md]
- Propagate with `?` (`File::open("hello.txt")?`, chained `read_to_string`, or `fs::read_to_string`); `?` works only in functions returning a compatible `Result` (or `Option` for `Option` values, never mixed), so give `main` the `Result<(), Box<dyn Error>>` shape with `Ok(())` at the end [src: ch09-propagating-errors.md]
- Return `Result` by default so callers decide (they may recover or turn it into `panic!`); panic in examples, prototypes, and tests (`unwrap` and `expect` mark a failure), when the team knows more than the compiler (a hardcoded valid input with its reason), and on broken contracts or bad states (out-of-bounds access, invalid external state) documented in the API; encode routine checks in types (`Option` versus a value, `u32` for non-negative, a validated `Guess` type whose `new` panics outside 1..100) [src: ch09-to-panic-or-not.md]

## Lifetimes

- When the borrow checker cannot infer a returned reference, annotate with `fn longest<'a>(x: &'a str, y: &'a str) -> &'a str`; the single `'a` tells the checker both inputs and the output live under `elision` failure [src: ch10-03-lifetime-syntax.md]

## Smart pointers

- Use `Box<T>` for a recursive type with a single owner (a `cons` list node holds `Box<List>`), because the box gives the value a known `size` on the heap [src: ch15-01-box.md]
- Use `Rc<T>` with `Rc::clone(&v)` for several immutable owners of one value on a single `thread`; the `reference count` frees the value when the last owner drops [src: ch15-04-rc.md]
- Use `RefCell<T>` (usually as `Rc<RefCell<T>>`) for several mutable owners on one thread; borrowing rules are then enforced at `runtime`, so a second `borrow_mut()` while borrowed panics instead of failing to compile [src: ch15-05-interior-mutability.md]

## Fix-first workflow

Compile the failing file with `rustc --edition 2021`, read the code (`E0382`, `E0502`, `E0004`, `E0277`), apply the matching rule above, and recompile. For programs that should compile (`?` propagation, `&str` slices, `Vec` and `HashMap` counts), also run the binary and check its stdout (`42`, `hello`, `3 2`). The per-code recipes are in `references/patterns.md` and the one-page reminder in `references/cheatsheet.md`.
