# Cheatsheet: sd-replace preview

One page. Every line replayed from the chmln/sd sources at `44febdf8`.

## Replace

| See | Branch |
|---|---|
| avoid regex escaping | `String-literal mode`, `-F` `fixed-strings`, no `backslashes` |
| simpler than sed | `sd before after`, `sed s/before/after/g`, `-A` `across mode` |
| strip specials | `-F`, `fixed-strings`, `lots of special chars` |
| number the parts | `capture groups`, `$1`, `named capture`, `dollars` |

## Files and modes

| Want | Type |
|---|---|
| fix empty dollars | `ambiguities`, `${var}`, `dollars_dollars` |
| see it first | `in-place`, `-p`, `preview`, `http.js` |
| match newlines | `line by line`, `-A`, `across`, `\n` |
| keep dash and dollar | `--`, `end of flags`, `$$`, `$bar` |

## Lines

| Want | Type |
|---|---|
| literal phrase | `fixed-strings` 1 line, first at line `114` with -F |
| preview wiring | `preview` 1 line, line `162` shows changes |
| across default | `across` 8 lines, line `29` requires -A |
| opener claim | `open_source` 2 lines, line `41` defines the opener |

## Prove the pin

| Replay | Prints |
|---|---|
| `rg -n "fixed-strings" work/sd-replace/src/README.md` | 1 match line, first at line `114` with literal mode |
| `rg -n "preview" work/sd-replace/src/README.md` | 1 match line, first at line `162` with preview |
| `rg -n "across" work/sd-replace/src/README.md` | 8 match lines, first at line `29` with across mode |
| `rg -n "open_source" work/sd-replace/src/input.rs` | 2 match lines, first at line `41` with the opener |
