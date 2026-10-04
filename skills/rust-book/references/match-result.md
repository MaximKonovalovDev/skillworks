# Exhaustive match and the ? operator (ch06-02, ch09-02)

Matches in Rust are exhaustive: every possible value must be covered. This rejected program handles `Some` but forgets `None`:

  let x: Option<i32> = None;
  match x { Some(v) => println!("{v}"), }

Live compiler output (rustc 1.97.1, 2026-10-04):

  error[E0004]: non-exhaustive patterns: `None` not covered

Sanctioned remedies: add the missing arm (`None => ...`), or add a catch-all arm last. Use `_` when the value is not needed; name it (for example `other`) when the arm uses the value. Arms evaluate in order, so the catch-all goes last.

The `?` operator is the ergonomic form of match-and-early-return for `Result`:

  let s = match fs::read_to_string(path) { Ok(s) => s, Err(e) => return Err(e), };
  let s = fs::read_to_string(path)?;

The rule for where `?` is allowed: only in functions whose return type is compatible with the value it unwraps, normally a `Result` (or `Option` for option values). Using `?` on a `Result` inside `fn main()` returning `()` does not compile. Verified live (rustc 1.97.1, 2026-10-04): a `?`-based `double_it("21")` program prints `42`.
