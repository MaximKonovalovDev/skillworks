# Cheatsheet: idiomatic Rust in one page

All lines replayed from fresh snippets on 2026-10-09.

| See | Write |
|---|---|
| const case | `UPPERCASE` like `MAX_SIZE`, never lowercase const |
| type case | `CamelCase` like `UserId`, never lowercase struct |
| fn case | `snake_case` like `user_id`, never uppercase fn |
| Option | `match` over `Some` and `None`, never `unwrap()` |
| Result | `Result` return with `question mark` operator, never `unwrap()` in libs |
| loop | `iter()` with `map` and `collect`, never `len()` index |
| build | `builder` steps `with_*` take `mut self` return `Self`, close `build()` |
| id type | `newtype` like `UserId` over bare `String` id |
| guard | `RAII` with `Drop` and `cleanup` in `drop` |
| extend | `extension trait` `trait Ext` plus `blanket` bound |
| text arg | `&str` never `&String`, slices as borrowed views |
| maybe owned | `Cow` for borrowed or owned, `let` first then `mut` |
| loop clone | borrow `&item` never `.clone()` in loop |
| poly global | no `Deref` poly, no `singleton` with `static mut`, tiny `unsafe` with safety |

## Prove the pin

ISBN `9781633437463` names the Manning book read 2026-10-09. Run `python skills/idiomatic-rust/scripts/idiomatic_rust.py` for 12 of 12 pairs behave as written.

