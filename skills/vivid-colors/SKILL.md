---
name: vivid-colors
description: Use when theming ls colors with vivid: LS_COLORS generation, bash and fish setup, 8-bit fallback, ansi palette, custom themes, molokai entries, RRGGBB spec, Apache-2.0 licence.
version: 0.1.0
author: skillworks
license: MIT
---

# LS_COLORS theming with vivid, the LS_COLORS generator

Rules distilled from sharkdp/vivid at `6f33cf1b` (master, read 2026-10-08) for the color-theme class: which export enables a theme, how fish differs, how 8-bit fallback works, which theme follows the terminal, where custom themes live, which molokai entries color dirs and links, and how RRGGBB replaces dircolors. Each rule names the exact token to branch on and the pair that replays it. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`. The runnable proof of every rule is `references/pairs.md` (machine list `references/pairs.json`), replayed by `scripts/run_vivid.py`.

## Generate and enable

- vivid is a `generator` for the `LS_COLORS` variable consumed by `ls` plus `fd` plus `tree` [src: references/pairs.md#vc-p01]
- The bash line is `export LS_COLORS="$(vivid generate molokai)"` placed in `bashrc` [src: references/pairs.md#vc-p02]
- The fish line is `set -gx LS_COLORS (vivid generate molokai)` since fish has no `export` [src: references/pairs.md#vc-p03]
- Old terminals fall back with `--color-mode 8-bit` (`-m 8-bit`) over the `truecolor` default [src: references/pairs.md#vc-p04]

## Palettes and themes

- The `ansi` theme reuses the terminal `16-color` palette so ls follows the `terminal theme` [src: references/pairs.md#vc-p05]
- Custom themes live in a `themes` `subfolder`, or pass an `explicit path` to generate [src: references/pairs.md#vc-p06]
- In molokai the `directory` entry is `cyan` and the `symlink` entry is `pink` under `core` [src: references/pairs.md#vc-p07]
- Colors use `RRGGBB` translated to `24-bit` or 8-bit codes, unlike `dircolors` one-file mixing [src: references/pairs.md#vc-p08]

## Lines and staged errors

- Line `36` of `README.md` shows the `export` line: the token appears 9 times starting at lines `6` and `36` [src: references/pairs.md#vc-p09]
- Line `27` of `molokai.yml` shows `foreground` cyan: the token appears 23 times starting at lines `27` and `30` [src: references/pairs.md#vc-p10]
- Line `36` of `README.md` shows `vivid generate` molokai: the token appears 5 times starting at lines `36` and `42` [src: references/pairs.md#vc-p11]
- Line `15` of `README.md` shows `RRGGBB`: the depth tokens appear 5 times across both files from line `15` [src: references/pairs.md#vc-p12]

## Prove the pin

Replayed live 2026-10-08 with the installed `rg` (each replay ends exit 0):

```
rg -n "LS_COLORS" work/vivid-colors/src/README.md
```

prints 9 match lines at lines `6`, `36`, `42`, `52`, `63`, `71`, `127`, `165` and `167` where line `36` exports LS_COLORS from vivid generate molokai. `rg -n "foreground" work/vivid-colors/src/molokai.yml` prints 23 match lines starting at lines 27, `30`, `35` and `39`, where line `27` sets directory foreground to cyan and line `30` sets symlink to pink. `rg -n "vivid generate" work/vivid-colors/src/README.md` prints 5 match lines at lines 36, `42`, `52`, `71` and `79`, where line `79` shows the explicit-path form. `rg -n "8-bit|truecolor|RRGGBB" work/vivid-colors/src/README.md work/vivid-colors/src/molokai.yml` prints 5 match lines with README line `15` giving RRGGBB and line `63` giving the -m 8-bit export.
