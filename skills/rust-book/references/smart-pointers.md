# Smart pointers: Box, Rc, RefCell (ch15-01, ch15-04, ch15-05)

Assign each scenario to its sanctioned pointer:

- Recursive type with a single owner, such as a `cons` list node holding the next node: use `Box<T>`. The box stores the data on the heap with a known size, which lets the recursive type compile.
- Several immutable owners of one value on a single thread, such as graph edges sharing nodes: use `Rc<T>` and share with `Rc::clone(&v)`. The reference count frees the value when the last owner drops. `Rc<T>` is not thread-safe; threads need `Arc<T>` instead.
- Several mutable owners of one value on a single thread: use `RefCell<T>`, normally combined as `Rc<RefCell<T>>`. `RefCell<T>` keeps single ownership but enforces the borrowing rules at runtime rather than at compile time.

The runtime trade-off: with `RefCell<T>`, calling `borrow_mut()` while a borrow is live panics at runtime instead of failing to compile. Prefer compile-time borrowing (`&`, `&mut`) wherever the borrow pattern is statically known, and reach for `RefCell<T>` only for interior mutability, such as shared test doubles or graph mutation through shared handles.
