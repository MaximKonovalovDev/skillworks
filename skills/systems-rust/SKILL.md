---
name: systems-rust
description: Use when writing or fixing Rust ownership, borrow-checker, concurrency, or C-interop code for the engine: moves, borrows, lifetimes, Box/Rc/Arc, scoped threads, Mutex discipline, unsafe and raw-pointer boundaries, C strings.
version: 0.1.0
author: skillworks
tags: []
license: MIT
---

# Systems Rust: ownership, borrows, threads, and C boundaries

Rules distilled from Programming Rust (Blandy, Orendorff, Tindall, 3rd edition early release, chapters 1 to 5: tour, types, ownership, references, expressions) for engine work. Each rule names the exact pattern and the chunk it came from. Scope: this source covers ownership through expressions, while the full concurrency and FFI chapters are absent from this early release, so the C rules below are boundary rules only. Detail lives beside this file in `glossary.md`, `patterns.md`, and `cheatsheet.md`, plus per-group notes in `references/`.

## Ownership and moves

- Every value has exactly one `owner`, and the value is `dropped` when the owner leaves scope. `i32` copies on assignment while `String` moves. [src: `0029.txt`]
- `let s2 = s1;` moves a `String`, so `s1` cannot be used afterwards. rustc rejects the use with `E0382` (`borrow of moved value`). Fix it with `s1.clone()` or borrow with `&s1`. [src: `0034.txt`]
- Only bit-for-bit copies may be `Copy`. `i32` qualifies, while `String`, `Box<T>`, `File`, and `MutexGuard` do not, since each owns a resource that drop must release. [src: `0034.txt`]
- A `Vec` deep-copies with `v.clone()`, duplicating the vector and its elements. [src: `0032.txt`]
- `let third = v[2];` is refused (`Cannot move out of index of Vec`). Borrow the element or clone it instead. [src: `0033.txt`]
- `Box::new(v)` moves `v` into the heap. The `Box` owns that space and frees it when dropped. [src: `0029.txt`]
- Share one value on a thread with `Rc::new` plus `s.clone()` to raise the count. `Arc` is the atomic twin for sharing across threads. [src: `0035.txt`]
- An `Rc` referent is assumed shared, so it must never be mutated through the `Rc`. [src: `0036.txt`]

## Borrows and lifetimes

- `&x` borrows a reference to `x`, and `*r` reads the value the reference points to. [src: `0005.txt`]
- Hold either one `&mut` reference or any number of `&` references, never both. A reference must never outlive its referent. [src: `0041.txt`]
- A second `&mut y` while `y` is mutably borrowed is refused (`cannot borrow as mutable more than once`). `y` cannot be used until the borrow ends. [src: `0047.txt`]
- Reborrowing shared from shared (`&r.0`) is allowed, while reborrowing shared as mutable (`&mut r.1`) is refused. From a mutable borrow, `&mut m.0` and a disjoint `&m.1` are allowed. [src: `0047.txt`]
- `clone_from(&mut f, &f)` is refused (`cannot borrow as immutable because it is also borrowed as mutable`). Exclusive mutable access forbids the alias. [src: `0047.txt`]
- References are never null, and integers never convert to references outside `unsafe` code. [src: `0039.txt`]
- A program that avoids `unsafe` is free of data races by construction, since no value can be both shared and mutable. [src: `0047.txt`]
- Tie an output lifetime to an input with `fn smallest<'a>(v: &'a [i32]) -> &'a i32`, so the result is known to live as long as the slice. [src: `0043.txt`]

## Scoped concurrency

- Guard shared data with a `Mutex`. Touch it only while holding the lock, which releases automatically when the guard drops. [src: `0008.txt`]
- Moving ownership of a structure to another thread relinquishes every sender-side access to it. [src: `0008.txt`]
- `std::thread::scope(|spawner| { ... })` waits for every spawned thread before it returns, so threads may borrow stack data. [src: `0015.txt`]
- `spawner.spawn(move || { ... })` moves the `band` slice into the thread, giving that thread sole use of it. [src: `0015.txt`]
- `pixels.chunks_mut(rows_per_band * bounds.0)` cuts the buffer into exclusive mutable bands, one band per thread. [src: `0015.txt`]
- Size the pool with `std::thread::available_parallelism().expect(...).get()` and round rows up with `div_ceil`. [src: `0014.txt`]

## C boundary rules

- `*const T` and `*mut T` raw pointers dereference only inside `unsafe` blocks. [src: `0021.txt`]
- `c"main"` is a `&std::ffi::CStr`, null-terminated for C APIs. Build one from bytes with `CStr::from_bytes_with_nul(b"main\0")`. [src: `0027.txt`]
- `b"\x7fELF"` is a `&[u8; 4]` byte string. It carries raw bytes with no UTF-8 promise. [src: `0027.txt`]
- `&str` must hold valid UTF-8 and `char` a valid scalar value. Only `unsafe` abuse can break the invariant. [src: `0025.txt`]

## Fix-first workflow

Compile the failing file with `rustc --edition 2021`, read the code (`E0382`, `E0499`), apply the matching rule above, and recompile. For programs that should build, run the binary and check its stdout.
