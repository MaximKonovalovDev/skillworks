# Cheatsheet

One owner per value, dropped at scope end. `i32` copies, `String` moves.

`let s2 = s1;` then `s1` is gone: `E0382`. Fix with `s1.clone()` or `&s1`.

Not `Copy`: `String`, `Box<T>`, `File`, `MutexGuard`. Drop has work to do.

`v.clone()` deep-copies a `Vec`. `v[2]` cannot move out; borrow or clone it.

`Box::new(v)` owns heap space. `Rc::new` plus `s.clone()` shares on a thread. `Arc` shares across threads.

One `&mut` or many `&`, never both. Borrows must never outlive the referent.

`&r.0` reborrows fine. `&mut r.1` from shared is refused. `clone_from(&mut f, &f)` is refused.

No `unsafe`, no data races: free by construction.

`fn smallest<'a>(v: &'a [i32]) -> &'a i32` ties output life to input.

`Mutex`: touch data only while holding the lock. Moving ownership across threads beats sharing.

`std::thread::scope` joins every thread. `spawner.spawn(move || { ... })` takes the `band`. `chunks_mut` cuts exclusive bands. `available_parallelism` plus `div_ceil` sizes them.

`*const T` and `*mut T` deref only in `unsafe`. `c"main"` is `&std::ffi::CStr`. `b"\x7fELF"` is `&[u8; 4]`.

Build check: `rustc --edition 2021 file.rs`. Read `E0382` and `E0499`, fix, recompile.
