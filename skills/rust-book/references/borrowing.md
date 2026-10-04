# Borrowing and dangling references (ch04-02)

The two rules of references, quoted short from the Rust book ch04-02: at any given time you can have either one mutable reference or any number of immutable references, and references must always be valid.

Broken example the book sanctions:

  let mut s = String::from("hello");
  let r1 = &s;
  let r2 = &mut s;
  println!("{r1}");

This breaks the first rule: `r2` is a mutable borrow while `r1`, an immutable borrow, is still used later. Live compiler output (rustc 1.97.1, 2026-10-04):

  error[E0502]: cannot borrow `s` as mutable because it is also borrowed as immutable

Sanctioned fix: end the immutable borrow before the mutable one, for example by closing the scope in which `r1` is used, then create `r2`. Multiple mutable references are likewise allowed only when they are not simultaneous.

Dangling rule: a reference must always point at valid data, so a function must never return a reference to a value it created. Return an owned `String`, or take the data as a function parameter with a lifetime (see lifetimes.md).
