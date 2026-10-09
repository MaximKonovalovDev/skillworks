# Ownership and moves

Facts for engine work, distilled from Programming Rust chapters 3 to 4 (chunks `0028.txt` to `0036.txt`). One owner per value, moves by default, shared ownership only through counted pointers.

Every value has exactly one owner, and the value drops when the owner leaves scope. A `Vec` owns its heap buffer, a struct owns its fields, and a `Box` owns the heap space it points to. This tree of ownership is what gives back prompt freeing without a collector.

Assignment moves non-`Copy` values. After `let s2 = s1;` the `String` belongs to `s2`, and any use of `s1` is rejected with `E0382` (borrow of moved value). The sanctioned fixes are `s1.clone()` and borrowing with `&s1`. Moves also apply to function arguments and struct fields.

`Copy` is reserved for bit-for-bit copies such as `i32`. `String`, `Box<T>`, `File`, and `MutexGuard` are not `Copy`, because each owns a resource that drop must release. A type that needs custom drop work can never be `Copy`.

Deep copies are explicit. `v.clone()` on a `Vec` duplicates the vector and its elements. Moving out of an index is refused (`Cannot move out of index of Vec`), so borrow the element or clone it instead.

Shared ownership uses counted pointers. `Rc::new` with `s.clone()` shares one value on a single thread, while `Arc` uses an atomic count so it can cross threads. The count frees the value when the last owner drops. An `Rc` referent is assumed shared and must never be mutated through the `Rc`.

Measured with rustc 1.x (`rustc --edition 2021`):

```rust
let s1 = String::from("hello");
let s2 = s1;
println!("{s1} {s2}");
```

prints `error[E0382]: borrow of moved value`, exit 1, and the help suggests `s1.clone()`.

```rust
let point = Box::new((0.625, 0.5));
println!("{point:?}");
```

prints `(0.625, 0.5)`, exit 0.

```rust
use std::rc::Rc;
let s: Rc<String> = Rc::new("shirataki".to_string());
let t = s.clone();
let u = s.clone();
println!("{} {} {}", Rc::strong_count(&s), t, u);
```

prints `3 shirataki shirataki`, exit 0.
