# Cheatsheet: hexyl-hex binary view

One page. Every line replayed from the sharkdp/hexyl sources at `6ecc29b9`.

## Viewer and install

| See | Branch |
|---|---|
| garbage from cat | `hex viewer`, `NULL bytes`, `printable ASCII`, `non-ASCII` |
| install from source | `Rust 1.56`, `cargo install hexyl`, `cargo install --path` |
| install on distros | `apt install hexyl`, `dpkg`, `apt-get install hexyl` |
| fix the colors | `environment variables`, `HEXYL_COLOR_ASCII_PRINTABLE`, `HEXYL_COLOR_NULL` |

## Colors and code

| Want | Type |
|---|---|
| spell a color | `bright blue`, `RGB hex`, `#abcdef` |
| trace the default | `COLOR_NULL`, `COLOR_NONASCII`, `BrightBlack`, `Yellow` |
| explain the override | `init_color`, `HEXYL_COLOR_`, `DynColors` |
| clear the slice | `Apache-2.0`, `MIT`, `at your option` |

## Lines

| Want | Type |
|---|---|
| viewer claim | `hex viewer` 1 line, first at line `7` with colored categories |
| color wiring | `HEXYL_COLOR` 8 lines, first at line `188` with printable entry |
| null claim | `NULL` 3 lines, first at line `5` with COLOR_NULL |
| printable claim | `ASCII_PRINTABLE` 3 lines, first at line `9` with the printable static |

## Prove the pin

| Replay | Prints |
|---|---|
| `rg -n "hex viewer" work/hexyl-hex/src/README.md` | 1 match line, first at line `7` with the viewer |
| `rg -n "HEXYL_COLOR" work/hexyl-hex/src/README.md` | 8 match lines, first at line `188` with config |
| `rg -n "NULL" work/hexyl-hex/src/colors.rs` | 3 match lines, first at line `5` with COLOR_NULL |
| `rg -n "ASCII_PRINTABLE" work/hexyl-hex/src/colors.rs` | 3 match lines, first at line `9` with the printable static |
