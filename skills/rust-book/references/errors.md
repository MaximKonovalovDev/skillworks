# Panic versus Result (ch09)

Own words distilled from the Rust book chapter on error handling. Only short code quotes are copied, each with its chapter.

## Unrecoverable errors: panic, unwind, backtrace

Stop the program with `panic!` when nothing can be done (`panic!("crash and burn")` prints `thread 'main' panicked` with the file and line, plus a note to set `RUST_BACKTRACE=1`). By default the program unwinds (walks back up the stack cleaning each frame); switch to immediate abort with `panic = 'abort'` in `Cargo.toml` for the smallest binary, leaving cleanup to the operating system.

Indexing `v[99]` on a 3-element vector panics (`index out of bounds: the len is 3 but the index is 99`): with `[]` there is no value to return, and refusing to continue protects against buffer overreads. Set `RUST_BACKTRACE=1`, read from the top until the first file the team wrote (line 6 of the trace points at line 4 of `src/main.rs` in the book example), and fix the action there instead of panicking.

## Recoverable errors: match, ErrorKind, unwrap, expect

`File::open` returns `Result<File, io::Error>` (`Ok(file)` or `Err(error)`); handle it with `match` (`Ok(file) => file`, `Err(error) => panic!`). Branch failure reasons with `error.kind()`: `ErrorKind::NotFound` creates the file (`File::create`), any other kind (`_`) panics. The closure form (`unwrap_or_else`) behaves the same with less nesting.

`unwrap` returns the `Ok` value or panics (`called Result::unwrap() on an Err value`); `expect` does the same with an own message (`hello.txt should be included in this project`). Production code prefers `expect` with context about why success was assumed.

## Propagating with ?

Return the error upward with `return Err(e)` (early return, caller decides) or with the `?` shortcut: `File::open("hello.txt")?` plus `read_to_string(&mut username)?` plus `Ok(username)`, chained calls, or the shortest `fs::read_to_string("hello.txt")`. The `?` on `Err` converts the error through `From` into the function return type.

`?` works only in functions returning a compatible type: `Result` for `Result` values, `Option` for `Option` values (never mixed; convert with `ok` or `ok_or`). Using `?` in `fn main()` returning `()` fails with `E0277` (`the ? operator can only be used in a function that returns Result or Option`); fix by returning `Result<(), Box<dyn Error>>` with `Ok(())` at the end (any error type fits, exit 0 on `Ok`, nonzero on `Err`). The one-line `text.lines().next()?.chars().last()` shows `?` on `Option`.

## Guidelines: return Result, panic on broken contracts

Return `Result` by default: the caller may recover, use a default, look elsewhere, or turn it into `panic!`. Panic in examples (a placeholder for real handling), prototypes (`unwrap` and `expect` mark what to harden later), and tests (a panic marks the failure). Panic when the team knows more than the compiler (a hardcoded `"127.0.0.1"` parsed with `expect` and its reason) and on broken contracts: unexpected bad states the rest of the code relies on not happening, invalid caller values, insecure continuations, or bad external states. Out-of-bounds access panics for this reason; document every panic in the API.

Encode routine checks in types instead of repeated runtime tests: a parameter of a plain type (not `Option`) needs no `None` arm, `u32` is never negative, and a validated `Guess` type (private `value` field, `new` that panics outside 1..100, public `value()` getter) lets signatures take `Guess` instead of `i32` with no further checks.

Verified live (rustc 1.97.1): a `?`-based parse-and-double program prints `42`.
