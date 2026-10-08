---
name: hexyl-hex
description: Use when viewing binary files with hexyl: hex viewer byte categories, cargo and apt installs, HEXYL_COLOR config, bright and RGB spellings, COLOR statics with init_color override, Apache-2.0 or MIT licence.
version: 0.1.0
author: skillworks
license: MIT
---

# Read binaries with hexyl, the colored hex viewer

Rules distilled from sharkdp/hexyl at `6ecc29b9` (main, read 2026-10-08) for the binary-read class: what the viewer shows, how source and distro installs spell, how colors configure, which statics map categories, how the env override parses, and which licence covers the slice. Each rule names the exact token to branch on and the pair that replays it. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`. The runnable proof of every rule is `references/pairs.md` (machine list `references/pairs.json`), replayed by `scripts/run_hexyl.py`.

## Viewer and installs

- hexyl is a `hex viewer` for the terminal; colored output splits `NULL bytes`, `printable ASCII`, whitespace, other ASCII and `non-ASCII` [src: references/pairs.md#hx-p01]
- Install from source on `Rust 1.56` or newer with `cargo install hexyl`, or clone plus `cargo install --path` [src: references/pairs.md#hx-p02]
- On Ubuntu 19.10 plus run `apt install hexyl`; older deb via `dpkg` plus `apt-get install hexyl` on Debian [src: references/pairs.md#hx-p03]
- Configure via `environment variables`; `HEXYL_COLOR_ASCII_PRINTABLE` covers printable and `HEXYL_COLOR_NULL` covers null [src: references/pairs.md#hx-p04]

## Colors and code

- Spell colors with `bright blue` names plus `RGB hex` format like `#abcdef` in the example [src: references/pairs.md#hx-p05]
- Statics `COLOR_NULL` plus `COLOR_NONASCII` default to `BrightBlack` plus `Yellow` for null and non-ASCII [src: references/pairs.md#hx-p06]
- `init_color` builds the name with `HEXYL_COLOR_` prefix and parses `DynColors` before default fallback [src: references/pairs.md#hx-p07]
- Offered under `Apache-2.0` plus `MIT` `at your option` for a permissive slice [src: references/pairs.md#hx-p08]

## Paths and staged errors

- Line `7` of `README.md` shows `hex viewer` output: the phrase appears 1 time at line `7` [src: references/pairs.md#hx-p09]
- Line `188` of `README.md` shows `HEXYL_COLOR` config: the token appears 8 times starting at lines `188` and `193` [src: references/pairs.md#hx-p10]
- Line `5` of `colors.rs` shows `NULL` statics: the token appears 3 times starting at lines `5` and `38` [src: references/pairs.md#hx-p11]
- Line `9` of `colors.rs` shows `ASCII_PRINTABLE` statics: the token appears 3 times starting at lines `9` and `48` [src: references/pairs.md#hx-p12]

## Prove the pin

Replayed live 2026-10-08 with the installed `rg` (each replay ends exit 0):

```
rg -n "hex viewer" work/hexyl-hex/src/README.md
```

prints 1 match line at line `7` where the viewer line names colored categories. `rg -n "HEXYL_COLOR" work/hexyl-hex/src/README.md` prints 8 match lines starting at lines 188, 193, and `197`, where line `188` opens the printable entry. `rg -n "NULL" work/hexyl-hex/src/colors.rs` prints 3 match lines starting at lines 5 and `38`, where line `5` defines COLOR_NULL. `rg -n "ASCII_PRINTABLE" work/hexyl-hex/src/colors.rs` prints 3 match lines starting at lines 9 and `48`, where line `9` defines COLOR_ASCII_PRINTABLE.
