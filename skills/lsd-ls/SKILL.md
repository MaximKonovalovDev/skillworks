---
name: lsd-ls
description: Use when listing directories with lsd: classify flags, tree views, git status, long tables, sorting, icon and config isolation, Apache-2.0 licence.
version: 0.1.0
author: skillworks
license: MIT
---

# Directory listing with lsd, the LSDeluxe ls rewrite

Rules distilled from lsd-rs/lsd at `4b6c14a1` (main, read 2026-10-08) for the directory-listing class: which alias spells a tree, which override kinds change icons, how git status reduces, how long tables name blocks, how depth bounds a tree, how sorts flip, where config lives, and how to isolate icons from config. Each rule names the exact token to branch on and the pair that replays it. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`. The runnable proof of every rule is `references/pairs.md` (machine list `references/pairs.json`), replayed by `scripts/run_lsd.py`.

## Aliases and icons

- Shell aliases live in the shell config with `lt` spelling `lsd --tree` for the one-keystroke tree view [src: references/pairs.md#ls-p01]
- Icon overrides come in 3 kinds with `filetype` for every directory plus `name` plus `extension` [src: references/pairs.md#ls-p02]
- The `--git` flag shows status where a directory is a `reduction` of file statuses computed `recursively` [src: references/pairs.md#ls-p03]
- The `--long` flag shows metadata as a `table` with `--blocks` naming the blocks and their order [src: references/pairs.md#ls-p04]

## Trees and sorts

- The `--tree` flag draws a tree while `--depth` stops it `recurs`ing past the given depth [src: references/pairs.md#ls-p05]
- Sort by time with `--timesort` or by size with `--sizesort`, and flip any order with `--reverse` [src: references/pairs.md#ls-p06]
- Point at a trial config with `--config-file`; the Unix default sits under `XDG_CONFIG_HOME` at `.config/lsd` [src: references/pairs.md#ls-p07]
- Isolate a broken setup with `--icon never` plus `--ignore-config` while colors ride on `LS_COLORS` [src: references/pairs.md#ls-p08]

## Paths and staged errors

- Line `116` of `lsd.md` shows the `--icon` default of `auto`: the token appears 5 times starting at lines `30` and `116` [src: references/pairs.md#ls-p09]
- Line `77` of `lsd.md` shows `--sizesort`: the `sort` token appears 9 times starting at lines `38` and `75` [src: references/pairs.md#ls-p10]
- Line `97` of `README.md` shows `alias l` as `lsd -l`: the `alias` token appears 8 times starting at lines `89` and `91` [src: references/pairs.md#ls-p11]
- Line `125` of `README.md` shows `XDG_CONFIG_HOME`: the config tokens appear 5 times across both files from line `125` [src: references/pairs.md#ls-p12]

## Prove the pin

Replayed live 2026-10-08 with the installed `rg` (each replay ends exit 0):

```
rg -n "icon" work/lsd-ls/src/lsd.md
```

prints 5 match lines at lines `30`, `116`, `117`, `119` and `120` where line `116` sets the --icon default to auto. `rg -n "sort" work/lsd-ls/src/lsd.md` prints 9 match lines at lines 38, `75`, `77`, `80`, `92`, `93`, `131`, `134` and `135`, where line `80` documents --timesort. `rg -n "alias" work/lsd-ls/src/README.md` prints 8 match lines at lines 89, `91`, `93`, `95`, `97`, `98`, `99` and `100`, where line `97` defines alias l as lsd -l. `rg -n "XDG_CONFIG_HOME|LS_COLORS" work/lsd-ls/src/README.md work/lsd-ls/src/lsd.md` prints 5 match lines with README line `125` giving $XDG_CONFIG_HOME/lsd and the lsd.md lines naming LS_COLORS plus XDG_CONFIG_HOME.
