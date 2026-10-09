# Borrows and lifetimes

Facts for engine work, distilled from Programming Rust chapter 4 (chunks `0036.txt` to `0048.txt`). References are non-owning pointers, and the borrow rules keep them safe.

`&x` borrows a reference to `x`, and `*r` reads the referent. References are never null, and integers never convert to references outside `unsafe` code. There is no default reference value, since no variable may be used before it is initialized.

The core rule: hold either one `&mut` reference or any number of `&` references, never both. A reference must never outlive its referent. A second `&mut y` while `y` is mutably borrowed is refused with `cannot borrow as mutable more than once`, and `y` cannot be used until the borrow ends.

Reborrowing follows the same split. Shared from shared (`&r.0`) is allowed, while shared as mutable (`&mut r.1`) is refused. From a mutable borrow, `&mut m.0` and a disjoint `&m.1` are allowed, but access through any other path stays forbidden while the reborrow lives.

The rules catch aliasing bugs at compile time. `clone_from(&mut f, &f)` is refused with `cannot borrow as immutable because it is also borrowed as mutable`, which is the same underlying mistake as self-assignment through two C++ handles or overlapping `memcpy` ranges.

A program that avoids `unsafe` is free of data races by construction, since no value can be both shared and mutable. Concurrency then rests on mutexes, channels, and atomics instead of on bare references.

Lifetimes name how long a borrow lives. `fn smallest<'a>(v: &'a [i32]) -> &'a i32` says the result lives exactly as long as the input slice. The `'a` parameter (pronounced tick-A) covers any lifetime the caller supplies.

Measured with rustc 1.x (`rustc --edition 2021`):

```rust
let mut y = 1;
let m1 = &mut y;
let m2 = &mut y;
println!("{m1} {m2}");
```

prints `error[E0499]: cannot borrow as mutable more than once`, exit 1.
