# Collections for engine lists and maps (ch08)

Own words distilled from the Rust book chapter on common collections. Only short code quotes are copied, each with its chapter.

## Vectors: engine entity lists

Build with `Vec::new()` (annotate the type when empty: `let v: Vec<i32> = Vec::new();`) or with `vec![1, 2, 3]` (the macro infers `Vec<i32>`). Grow with `push` (needs `mut`) and remove the last element with `pop`, which returns it.

Read one element two ways: `&v[2]` gives a reference (`let third: &i32 = &v[2];`), while `v.get(2)` gives `Option<&T>` to match (`Some(third)` or `None`). Indexing past the end with `[]` panics (`index out of bounds`) and is the right choice when the index must exist; `get` returns `None` and suits user-supplied indices that may be wrong.

Never hold `&v[0]` across a `push`: growing may reallocate and copy the contents elsewhere, so the old reference would dangle. The checker rejects it with `E0502` (`cannot borrow as mutable`). Iterate with `for i in &v` (shared) or `for i in &mut v` with `*i +=` (exclusive, dereference first); inserting or removing inside the loop borrows the whole vector and fails the same way. Mixed-type rows work through one enum (`SpreadsheetCell::Int`, `Float`, `Text`) plus an exhaustive `match`. Dropping the vector drops its elements, and references stay valid only while the vector lives.

## Strings: UTF-8 text, not indexable

`String` is a growable, mutable, owned UTF-8 string (a wrapper over bytes); `&str` is the borrowed slice, and literals live in the binary. Create with `String::new()`, `to_string()` (any `Display` type), or `String::from`.

Append a slice with `push_str` (takes `&str`, so `s2` stays usable and printable after) and one character with `push`. Join with `+` (calls `add(self, s: &str)`: moves the left side, coerces `&String` to `&str`, keeps the right side) or with `format!` (borrows everything, clearer for many parts).

Indexing is refused (`s1[0]` fails with `E0277`): lengths count bytes, one character may take several bytes, and indexing must stay constant-time. Slice by byte ranges (`&hello[0..4]`) only on character boundaries; a mid-character slice panics (`byte index 1 is not a char boundary`). Iterate with `chars()` for scalar values or `bytes()` for raw `u8`; grapheme clusters need a crate. Search with `contains` and substitute with `replace`.

## Hash maps: engine score and component maps

Map with `HashMap::new()` plus `use std::collections::HashMap` (not in the prelude, no construction macro). Keys and values share one type each. Read with `get(&key).copied().unwrap_or(0)` (`get` returns `Option<&V>`); iterate with `for (key, value) in &scores` in arbitrary order.

`insert` moves owned `String` keys and values (they are invalid after the call; `Copy` types such as `i32` copy instead) and overwrites the old value for a repeated key. `entry(key).or_insert(50)` inserts only when the key is absent and returns `&mut V`: check-then-insert in one call that pleases the borrow checker. Count words by `map.entry(word).or_insert(0)` plus `*count += 1` (dereference the mutable reference; it ends with the loop). The default hasher trades speed for resistance to hash-table denial of service; swap the hasher only after profiling.

Verified live (rustc 1.97.1): a `Vec` plus `HashMap` word-count program prints `3 2` for three words with two `hello` entries.
