# Slices as parameters (ch04-03)

The book rewrites the example from `fn first_word(s: &String) -> &str` to the sanctioned signature:

  fn first_word(s: &str) -> &str

What this buys the caller: the same function now accepts both `&String` values (as a slice of the whole string) and `&str` string literals directly. The generality comes free through deref coercion, which the book covers in Chapter 15: a `&String` coerces to `&str` at the call site.

Rule of thumb from the chapter: when a function only reads string data, take `&str`, never `&String`. The same idea generalises to slices: prefer `&[i32]` over `&Vec<i32>` so arrays and vectors both work.

Verified live (rustc 1.97.1, 2026-10-04): the `&str` version compiles clean and `first_word("hello world")` prints `hello`.
