# C boundary rules

Facts for engine work, distilled from Programming Rust chapters 2 to 4 (chunks `0021.txt`, `0025.txt`, `0027.txt`, `0039.txt`). Scope: the full unsafe and foreign-function chapters are absent from this early release, so these are boundary rules only. Anything beyond them needs source.

Raw pointers are C pointers with the safety off. `*const T` and `*mut T` dereference only inside `unsafe` blocks, which opt out of the safety guarantees. They appear when calling into a C library or when building a new data structure from scratch.

Rust types carry invariants the implementation enforces. `&str` must hold well-formed UTF-8 and `char` a valid Unicode scalar value, and only `unsafe` abuse can break those promises. Programs may therefore rely on them without rechecking.

C strings are null-terminated for C APIs. `c"main"` is a `&std::ffi::CStr`, stored with an extra zero byte. Build one from bytes with `CStr::from_bytes_with_nul(b"main\0")`, which checks the terminator and the absence of interior zeros.

Byte strings are bytes, not text. `b"\x7fELF"` is a `&[u8; 4]`, a reference to an immutable array of bytes, and it never promises valid UTF-8. The example is the magic number at the start of Linux executables, including release builds from `cargo build`.

Related boundaries: references are never null, integers never convert to references outside `unsafe` code, and mutable statics may only be touched inside an `unsafe` block because any thread can reach them.
