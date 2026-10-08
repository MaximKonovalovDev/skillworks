# Cheatsheet: delta-diff reading

One page. Every line replayed from the dandavison/delta sources at `3c2269c6`.

## Read

| See | Branch |
|---|---|
| what is delta | `syntax-highlighting pager`, `git` `diff` `grep` plus blame, reads only |
| wire into git | `pager = delta`, `diffFilter` to `delta --color-only` |
| words changed | `Word-level`, `Levenshtein`, `edit inference` |
| wide monitor | `side-by-side = true`, `line-numbers`, `wraps` |

## Move and style

| Want | Type |
|---|---|
| jump between diffs | `navigate`, `n and N`, `diff sections`, log -p |
| numbers in panels | `side-by-side`, `line-numbers`, `left-format` |
| dark themes | `bat`, `show-syntax-themes`, `dark` |
| conflicts and blame | `zdiff3`, `blame`, `hyperlinks` plus syntax highlighting |

## Lines

| Want | Type |
|---|---|
| panel phrase | `side-by-side` 4 lines, first at line `86` with line-numbers |
| jump wiring | `navigate` 3 lines, line `28` sets true for n and N |
| numbers default | `line-numbers` 3 lines, line `26` enables the feature |
| styling claim | `syntax highlighting` 3 lines, line `49` names bat themes |

## Prove the pin

| Replay | Prints |
|---|---|
| `rg -n "side-by-side" work/delta-diff/src/README.md` | 4 match lines, first at line `86` with line-numbers |
| `rg -n "navigate" work/delta-diff/src/README.md` | 3 match lines, first at line `28` with n and N |
| `rg -n "line-numbers" work/delta-diff/src/side_by_side.rs` | 3 match lines, first at line `26` with the feature |
| `rg -n "syntax highlighting" work/delta-diff/src/README.md` | 3 match lines, first at line `49` with bat themes |
