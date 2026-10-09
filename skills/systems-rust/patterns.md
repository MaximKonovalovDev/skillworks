# Patterns

Move-then-fix: when rustc prints `E0382` (borrow of moved value), clone the source with `s1.clone()` or borrow it with `&s1`. Never use a moved `String` again.

Copy check: before deriving or assuming `Copy`, ask whether drop has work to do. Buffers, handles, and guards (`String`, `Box<T>`, `File`, `MutexGuard`) are never `Copy`.

Share on one thread: wrap the value with `Rc::new`, hand out `s.clone()` handles, and let the last drop free it. Never mutate through the `Rc`. Cross threads only with `Arc`.

Borrow split: default to shared `&` borrows. Take a single `&mut` only for the mutation window, end it, then share again. Reborrow `&r.0` freely, but never `&mut r.1` from a shared borrow.

Alias refusal: treat `cannot borrow as immutable because it is also borrowed as mutable` as a real bug, not a lint to silence. Restructure the call, as with `clone_from(&mut f, &f)`.

Lifetime tie: when a function returns a borrow of its input, name one lifetime (`fn smallest<'a>(v: &'a [i32]) -> &'a i32`) instead of copying the data.

Bands and scope: split the buffer with `pixels.chunks_mut(rows_per_band * bounds.0)`, size the pool with `std::thread::available_parallelism().expect(...).get()` plus `div_ceil`, and run each `band` under `std::thread::scope` with `spawner.spawn(move || { ... })`.

Lock discipline: hold a `Mutex` guard for the shortest span that covers the mutation, and let the guard drop unlock. Move ownership across threads instead of sharing whenever the design allows it.

C handoff: pass `c"..."` literals or `CStr::from_bytes_with_nul` values to C APIs. Keep raw `*const T` and `*mut T` dereferences inside small `unsafe` blocks at the boundary, and keep the rest of the program in safe Rust.
