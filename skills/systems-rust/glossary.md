# Glossary

Owner: the single variable, field, or element that controls a value and drops it at scope end.

Move: transfer of ownership, as in `let s2 = s1;`. The source can no longer be used.

Copy: a bit-for-bit duplicate allowed only for types like `i32` with no drop work. `String`, `Box<T>`, `File`, and `MutexGuard` are not `Copy`.

Clone: an explicit deep copy, as in `v.clone()` for a `Vec` and `s.clone()` for an `Rc`.

Borrow: a non-owning reference. `&x` shares, `&mut y` mutates exclusively, and `*r` reads the referent.

Lifetime: the span a borrow is valid for, written `'a` as in `fn smallest<'a>(v: &'a [i32]) -> &'a i32`.

Box: `Box::new(v)` moves a value into owned heap space, freed when the box drops.

Rc: a single-thread counted pointer from `Rc::new`. Arc is the atomic twin for sharing across threads.

Mutex: a lock guarding shared data. Touch the data only while holding the lock.

Scoped thread: a thread from `spawner.spawn(move || { ... })` inside `std::thread::scope`, joined before the scope returns.

Band: one exclusive mutable slice from `pixels.chunks_mut(rows_per_band * bounds.0)`, owned by a single thread.

Raw pointer: `*const T` or `*mut T`, dereferenced only inside `unsafe` blocks.

CStr: `&std::ffi::CStr`, a null-terminated string for C APIs, built with `CStr::from_bytes_with_nul`.

Data race: simultaneous shared and mutable access from two threads. Safe Rust is free of data races by construction.
