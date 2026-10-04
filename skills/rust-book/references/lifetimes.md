# Lifetimes and the borrow checker (ch10-03)

The borrow checker rejects a `longest` function over two `&str` inputs with no annotations, because the elision rules cannot decide which input lifetime the returned reference follows: with two input lifetimes neither the single-input rule nor the `&self` method rule applies, so the output lifetime stays unknown.

Sanctioned signature from the chapter: tie both inputs and the output to one lifetime parameter.

  fn longest<'a>(x: &'a str, y: &'a str) -> &'a str

The single `'a` is the contract: the returned reference lives no longer than the shorter of the two inputs, and the caller must keep both inputs alive while using the result.

Related facts: lifetime names for struct fields are declared after `impl` and used after the struct name; elision still covers method signatures where one parameter is `&self`. String literals carry the `'static` lifetime, but do not reach for `'static` to silence an error unless the reference truly lives for the whole program.
