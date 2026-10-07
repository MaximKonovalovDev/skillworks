---
name: bat-cat
description: Use when reading files with bat: cat clone paging, pager precedence with BAT_PAGER, PagerSource plus PagerKind, from_bin mapping, and the exact lines to check.
version: 0.1.0
author: skillworks
license: MIT
---

# Read files with bat, the paging cat clone

Rules distilled from sharkdp/bat at `d9559c69` (master, read 2026-10-07) for the paged-read class: what bat is, when it pages, what it prints in a pipe, which flag shows numbers only, which variable wins the pager, and which enums classify the choice. Each rule names the exact token to branch on and the pair that replays it. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`. The runnable proof of every rule is `references/pairs.md` (machine list `references/pairs.json`), replayed by `scripts/run_bat.py`.

## Bat first, then the pager

- bat is a `cat(1)` clone with `syntax highlighting` and `Git integration`: never call it an editor, it only reads and never rewrites files [src: references/pairs.md#bt-p01]
- By default bat `pipes its own output to a pager` (example `less`): pass `--paging=never` on the command line or in config to work like `cat` always [src: references/pairs.md#bt-p02]
- On a `non-interactive terminal` bat acts as a `drop-in replacement for cat` and prints the `plain file contents`: piped output loses styling regardless of `--pager` [src: references/pairs.md#bt-p03]
- Run `bat -n` to show `line numbers` only with no grid and no header: the `-n` flag controls numbers-only output [src: references/pairs.md#bt-p04]

## Pager choice and precedence

- `BAT_PAGER` will `override` what is set in `PAGER`: the value `builtin` selects the builtin pager, empty disables paging [src: references/pairs.md#bt-p05]
- Read the choice origin in `PagerSource`: `EnvVarBatPager` for `BAT_PAGER`, `EnvVarPager` for `PAGER`, plus `Config` and `Default` [src: references/pairs.md#bt-p06]
- Read the known pagers in `PagerKind`: `Bat` plus `Less` plus `More` plus `Most` plus `Builtin`, with `Unknown` for anything unrecognised [src: references/pairs.md#bt-p07]
- Map names with `from_bin`: the string `less` maps to `Less`, `builtin` maps to `Builtin`, the current bat binary maps to `Bat` [src: references/pairs.md#bt-p08]

## Paths and staged errors

- Line `6` of `README.md` names bat a `cat(1)` clone with `syntax highlighting`: the phrase appears 9 times starting at lines `6`, `24`, and `137` [src: references/pairs.md#bt-p09]
- Line `94` runs `bat -n` for `line numbers` only: the phrase appears 7 times starting at lines `94`, `170`, and `506` [src: references/pairs.md#bt-p10]
- Line `6` of `pager.rs` defines `PagerSource`: the `Pager` word appears 28 times, the first three at lines `6`, `11`, and `14` [src: references/pairs.md#bt-p11]
- Line `647` sets `BAT_PAGER` to `builtin`: the variable appears 7 times, the first three at lines `647`, `650`, and `656` [src: references/pairs.md#bt-p12]

## Prove the pin

Replayed live 2026-10-07 with the installed `rg` (each replay ends exit 0):

```
rg -n "syntax highlighting" work/bat-cat/src/README.md
```

prints 9 match lines, the first three at lines 6, 24, and `137`, where line `6` calls bat a `cat(1)` clone with `syntax highlighting` and `Git integration`. `rg -n "line numbers" work/bat-cat/src/README.md` prints 7 match lines starting at lines 94, 170, and `506`, where line `94` runs `bat -n`. `rg -n Pager work/bat-cat/src/pager.rs` prints 28 match lines starting at lines 6, 11, and `14`, where line `6` defines `PagerSource`. `rg -n BAT_PAGER work/bat-cat/src/README.md` prints 7 match lines starting at lines 647, 650, and `656`, where line `647` sets `BAT_PAGER` to `builtin`.
