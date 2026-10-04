---
name: rust-book
description: Use when fixing a Rust borrow-checker or ownership rejection (moved value, mutable plus immutable borrow clash, non-exhaustive match, missing lifetime, ? in the wrong function) or when choosing Box, Rc, or RefCell: exact error codes, the book-sanctioned fix, and the signatures to write.
version: 1.0.0
author: skillworks
license: MIT
---

# Rust ownership and borrow-checker fixes

Fix-first rules distilled from the Rust book chapters on ownership, borrowing, slices, match, Result, lifetimes, and smart pointers. Each rule names the exact compiler code and the sanctioned fix. Longer notes live in `references/`: per-group facts, `glossary.md`, `patterns.md`, and `cheatsheet.md`.

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

## Lifetimes

- When the borrow checker cannot infer a returned reference, annotate with `fn longest<'a>(x: &'a str, y: &'a str) -> &'a str`; the single `'a` tells the checker both inputs and the output live under `elision` failure [src: ch10-03-lifetime-syntax.md]

## Smart pointers

- Use `Box<T>` for a recursive type with a single owner (a `cons` list node holds `Box<List>`), because the box gives the value a known `size` on the heap [src: ch15-01-box.md]
- Use `Rc<T>` with `Rc::clone(&v)` for several immutable owners of one value on a single `thread`; the `reference count` frees the value when the last owner drops [src: ch15-04-rc.md]
- Use `RefCell<T>` (usually as `Rc<RefCell<T>>`) for several mutable owners on one thread; borrowing rules are then enforced at `runtime`, so a second `borrow_mut()` while borrowed panics instead of failing to compile [src: ch15-05-interior-mutability.md]

## Fix-first workflow

Compile the failing file with `rustc --edition 2021`, read the code (`E0382`, `E0502`, `E0004`), apply the matching rule above, and recompile. For programs that should compile (`?` propagation, `&str` slices), also run the binary and check its stdout (`42`, `hello`). The per-code recipes are in `references/patterns.md` and the one-page reminder in `references/cheatsheet.md`.
