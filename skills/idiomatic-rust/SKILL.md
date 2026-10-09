---
name: idiomatic-rust
description: Use when writing or reviewing Rust code to match community idioms: naming, borrowing, iterators, error handling, builder and newtype patterns, and avoiding unwrap, clone, Deref and singleton traps with exact checks to run.
version: 0.1.0
author: skillworks
license: MIT
---

# Idiomatic Rust the Rustacean way

Rules distilled from Brenden Matthews, Idiomatic Rust: Code like a Rustacean (Manning 2024, ISBN `9781633437463`) for Rust code that reads like the community writes it. Each rule names the exact token to branch on and the pair that replays it. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`. The runnable proof of every rule is `references/pairs.md` (machine list `references/pairs.json`), replayed by `scripts/idiomatic_rust.py`.

## Names and flow

- Write constants and globals in `UPPERCASE` with underscores like `MAX_SIZE`, types in `CamelCase` like `UserId`, and variables plus functions in `snake_case` like `user_id`: a lowercase `const` or a `CamelCase` function name fails the check [src: references/pairs.md#ir-p01]
- Unwrap an `Option` with `match` or `if let`, never with `unwrap()`: the `match` arm names `Some` and `None`, the fixer keeps the `None` path [src: references/pairs.md#ir-p02]
- Propagate a `Result` with the `question mark` operator `?` from a function that returns `Result`: library code with `unwrap()` on `Err` becomes a `?` plus an early return [src: references/pairs.md#ir-p03]
- Prefer `iter()` plus adapters like `map` and `collect` over an index loop with `v[i]`: the `for` line holds `iter()` and no `len()` index read [src: references/pairs.md#ir-p04]

## Building blocks

- Build with a `builder` that chains `with_*` calls, each taking `mut self` and returning `Self`: the chain ends with `build()` and no `&mut self` setter that returns `()` [src: references/pairs.md#ir-p05]
- Wrap a single value in a `newtype` tuple struct like `struct UserId(String);`: the wrapper type carries the `newtype` name where a bare `String` id stood [src: references/pairs.md#ir-p06]
- Tie cleanup to ownership with `RAII` by implementing `Drop`: the `impl Drop` block calls the `cleanup` step the manual call forgot [src: references/pairs.md#ir-p07]
- Extend a foreign type with an `extension trait` and share behavior with a `blanket` impl like `impl<T: Clone> Ext for T`: the `trait Ext` line plus the `blanket` bound replace the inherent patch [src: references/pairs.md#ir-p08]

## Borrowing and avoidance

- Take borrowed text as `&str` and borrowed slices as `&[T]`, never as `&String` or `&Vec<T>`: the signature shows `&str` where the caller passes either form [src: references/pairs.md#ir-p09]
- Hold maybe-owned text in `Cow` and default to immutable bindings with `let`, adding `mut` only where written: the `Cow` import covers the borrowed-or-owned branch [src: references/pairs.md#ir-p10]
- Pass a `clone` only when ownership must move; inside a loop borrow with `&` instead of cloning each turn: the fixed loop shows `&item` where the slow one showed `.clone()` [src: references/pairs.md#ir-p11]
- Never use `Deref` to fake polymorphism, never hide mutable state in a `singleton` with `static mut`, and keep `unsafe` to a few lines with a safety comment: the clean file shows no `Deref` impl, no `static mut`, and a tiny `unsafe` block [src: references/pairs.md#ir-p12]

## Prove the file

Check one snippet from this skill folder:

```
python skills/idiomatic-rust/scripts/idiomatic_rust.py --check snippets/ir-p01-good.rs
```

prints `PASS ir-p01 UPPERCASE` and exit 0. The bad twin prints `FAIL ir-p01 lowercase const` and exit 1. Every pair in `references/pairs.md` replays the same way through `scripts/idiomatic_rust.py`.

