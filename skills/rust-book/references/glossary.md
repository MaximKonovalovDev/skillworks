# Glossary

- Borrow: temporary access through `&` (shared) or `&mut` (exclusive); the owner keeps ownership.
- Borrow checker: the compiler pass that rejects dangling references, use-after-move, and conflicting borrows.
- Catch-all arm: the final `match` arm (`_` or a named binding) that covers every value not matched earlier.
- Copy: a trait for stack-only types such as `i32`; assignment copies instead of moving.
- Dangling reference: a reference pointing at freed data; the compiler refuses to create one.
- Deref coercion: automatic conversion such as `&String` to `&str` at function calls.
- Elision: the three rules letting simple function signatures omit lifetime annotations.
- Exhaustive: a `match` covering every possible value of its type; non-exhaustive matches fail with `E0004`.
- Interior mutability: mutating through a shared reference via `RefCell<T>`, checked at runtime.
- Lifetime: the region of code a reference stays valid, written `'a`; `'static` means the whole program.
- Move: transfer of ownership, for example `let s2 = s1;`; the source binding becomes invalid.
- Owner: the single binding responsible for a value; the value drops when the owner goes out of scope.
- Reference count: the `Rc<T>` counter that frees shared data when the last owner drops.
- Slice: an unsized view such as `&str` or `&[i32]` into a contiguous sequence.
- Smart pointer: a struct acting like a pointer with extra metadata, such as `Box<T>`, `Rc<T>`, `RefCell<T>`.
