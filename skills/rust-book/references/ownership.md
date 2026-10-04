# Ownership and move (ch04-01)

The three ownership rules, quoted short from the Rust book ch04-01: each value has an owner, only one owner at a time, and the value is dropped when the owner goes out of scope.

Move example the book sanctions: `let s1 = String::from("hello"); let s2 = s1;` moves ownership, so `println!("{s1}")` is rejected. Live compiler output (rustc 1.97.1, 2026-10-04):

  error[E0382]: borrow of moved value: `s1`

Sanctioned fixes: call `s1.clone()` to deep-copy the heap data, or change the use to borrow (`&s1`) so ownership never moves. `Copy` types such as `i32` copy on assignment and never move.

Scope rule: a value created in a block is dropped at the closing brace; returning a reference to it is the dangling case covered in borrowing.md.
