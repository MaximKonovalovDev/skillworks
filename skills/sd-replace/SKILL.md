---
name: sd-replace
description: Use when replacing text with sd: string-literal mode, fixed-strings, sed-shape spelling, capture groups with dollar refs, preview with in-place, across mode, dash and dollar escapes.
version: 0.1.0
author: skillworks
license: MIT
---

# Replace text with sd, the preview-first replacer

Rules distilled from chmln/sd at `44febdf8` (main, read 2026-10-08) for the sed-replace preview class: what literal mode is, how sd beats sed, how groups spell, how files preview, how lines split, and how dashes plus dollars survive. Each rule names the exact token to branch on and the pair that replays it. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`. The runnable proof of every rule is `references/pairs.md` (machine list `references/pairs.json`), replayed by `scripts/run_sd.py`.

## Literal first, then the sed shape

- sd has a `String-literal mode` with `-F` or `fixed-strings` and no `backslashes` escaping pain [src: references/pairs.md#sd-p01]
- Write `sd before after` instead of `sed s/before/after/g`; the newline case needs `-A` plus `across mode` [src: references/pairs.md#sd-p02]
- Pass `-F` with `fixed-strings` on the `lots of special chars` example to strip without regex [src: references/pairs.md#sd-p03]
- Number parts with `capture groups` and `$1` refs; the `named capture` example yields `dollars` and cents [src: references/pairs.md#sd-p04]

## Groups, files, and modes

- Resolve `ambiguities` with `${var}` braces when `dollars_dollars` prints empty [src: references/pairs.md#sd-p05]
- Bare sd edits `http.js` `in-place`; add `-p` to `preview` the change first [src: references/pairs.md#sd-p06]
- Default is `line by line` so `\n` never matches; use `-A` plus `across` to join lines [src: references/pairs.md#sd-p07]
- Put `--` for `end of flags` so dash args survive; double `$$` to print `$bar` [src: references/pairs.md#sd-p08]

## Paths and staged errors

- Line `114` of `README.md` shows `fixed-strings` literal mode: the phrase appears 1 time at line `114` [src: references/pairs.md#sd-p09]
- Line `162` of `README.md` shows `preview` changes: the word appears 1 time at line `162` [src: references/pairs.md#sd-p10]
- Line `29` of `README.md` shows `across` mode: the word appears 8 times starting at lines `29`, `83`, and `87` [src: references/pairs.md#sd-p11]
- Line `41` of `input.rs` defines `open_source`: the token appears 2 times starting at lines `41` and `55` [src: references/pairs.md#sd-p12]

## Prove the pin

Replayed live 2026-10-08 with the installed `rg` (each replay ends exit 0):

```
rg -n "fixed-strings" work/sd-replace/src/README.md
```

prints 1 match line at line `114` where literal mode uses `-F` plus `--fixed-strings`. `rg -n "preview" work/sd-replace/src/README.md` prints 1 match line at line `162` where preview changes. `rg -n "across" work/sd-replace/src/README.md` prints 8 match lines starting at lines 29, 83, and `87`, where line `29` requires across mode. `rg -n "open_source" work/sd-replace/src/input.rs` prints 2 match lines starting at lines 41 and `55`, where line `41` defines open_source.
