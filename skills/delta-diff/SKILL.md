---
name: delta-diff
description: Use when reading git diffs with delta: syntax pager wiring, side-by-side with navigate and line numbers, word-level highlight, themes, blame and conflict styling.
version: 0.1.0
author: skillworks
license: MIT
---

# Read diffs with delta, the syntax pager

Rules distilled from dandavison/delta at `3c2269c6` (main, read 2026-10-07) for the diff-read class: what delta is, how git pages through it, how words light up, how the two-panel view wraps, how to jump, which feature the panel enables, where themes come from, and how conflicts plus blame improve. Each rule names the exact token to branch on and the pair that replays it. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`. The runnable proof of every rule is `references/pairs.md` (machine list `references/pairs.json`), replayed by `scripts/run_delta.py`.

## Delta first, then the wiring

- delta is a `syntax-highlighting pager` for `git` plus `diff` plus `grep` output and blame: never call it a rewrite tool, it only pages and styles and never edits files [src: references/pairs.md#dd-p01]
- Set `pager = delta` in core plus `diffFilter` to `delta --color-only`: the first pages every diff, the second filters interactive diffs [src: references/pairs.md#dd-p02]
- Highlight runs at `Word-level` with the `Levenshtein` `edit inference` between minus and plus lines: it lights the changed words only [src: references/pairs.md#dd-p03]
- Set `side-by-side = true` for the two-panel view with `line-numbers` on by default: long lines `wraps` instead of truncating [src: references/pairs.md#dd-p04]

## Navigate, features, and styling

- Set `navigate` to true then press `n and N` to jump between `diff sections`: the same binding serves log -p views [src: references/pairs.md#dd-p05]
- The panel enables the `line-numbers` builtin with `left-format` columns: `line-numbers-left-format` plus the right-format key own the two number columns [src: references/pairs.md#dd-p06]
- Themes come from `bat`: list them with `show-syntax-themes` and preview the `dark` set for night diffs [src: references/pairs.md#dd-p07]
- Set conflictStyle to `zdiff3` and read `blame` with `hyperlinks`: blame gains styling plus terminal links to the host [src: references/pairs.md#dd-p08]

## Paths and staged errors

- Line `86` of `README.md` shows delta with `side-by-side` and line-numbers: the phrase appears 4 times starting at lines `86`, `153`, and `157` [src: references/pairs.md#dd-p09]
- Line `28` sets `navigate` to true for n and N: the word appears 3 times starting at lines `28`, `40`, and `53` [src: references/pairs.md#dd-p10]
- Line `26` of `side_by_side.rs` enables `line-numbers` as a feature: the token appears 3 times starting at lines `26`, `27`, and `28` [src: references/pairs.md#dd-p11]
- Line `49` names `syntax highlighting` with the bat themes: the phrase appears 3 times starting at lines `49`, `55`, and `160` [src: references/pairs.md#dd-p12]

## Prove the pin

Replayed live 2026-10-07 with the installed `rg` (each replay ends exit 0):

```
rg -n "side-by-side" work/delta-diff/src/README.md
```

prints 4 match lines, the first three at lines 86, 153, and `157`, where line `86` shows delta with `side-by-side` and `line-numbers`. `rg -n "navigate" work/delta-diff/src/README.md` prints 3 match lines starting at lines 28, 40, and `53`, where line `28` sets `navigate` to true. `rg -n "line-numbers" work/delta-diff/src/side_by_side.rs` prints 3 match lines starting at lines 26, 27, and `28`, where line `26` enables `line-numbers`. `rg -n "syntax highlighting" work/delta-diff/src/README.md` prints 3 match lines starting at lines 49, 55, and `160`, where line `49` names `syntax highlighting` with bat themes.
