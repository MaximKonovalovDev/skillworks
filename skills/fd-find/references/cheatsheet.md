# Cheatsheet: fd file-find scoping

One page. Every line checked against fd at `14dcd92f`.

## Skips and reversals

| Want | Type |
|---|---|
| hidden files | `fd -H pattern` |
| ignored files | `fd -I pattern` |
| absolutely everything | `fd -HI pattern` or `fd -u pattern` |
| back to skipping hidden | `fd --no-hidden` |
| back to respecting ignores | `fd --ignore` |

## Match kind

| Want | Type |
|---|---|
| regex (default) | `fd '^x.*rc$'` |
| exact filename | `fd -g 'libc.so'` |
| literal substring | `fd -F 'a.b'` |
| full path | `fd -p '.*/lesson-[0-9]+/'` |
| multi-component glob | `fd -u -p -g '**/.git/config'` |

## Narrow

| Want | Type |
|---|---|
| by extension | `fd -e md` / `fd -e rs mod` |
| files only | `fd -t f` (`-tf`) |
| directories only | `fd -t d` (`-td`) |
| executables | `fd -tx` (implies file) |
| empty nowrap | `fd -te -tf` files, `fd -te -td` dirs |
| case-sensitive | `fd -s` |
| case-insensitive | `fd -i` |

## Act and prune

| Want | Type |
|---|---|
| per result | `fd -e zip -x unzip` |
| batched | `fd -g 'test_*.py' -X vim` |
| convert | `fd -e jpg -x convert {} {.}.png` |
| list details | `fd -l` |
| prune glob | `fd -E '*.bak'` |
| hidden minus git | `fd -H -E .git` |

## Arity

| Want | Type |
|---|---|
| current tree | `fd pattern` |
| one root | `fd pattern path` |
| everything | `fd` |
| catch-all in dir | `fd . dir` or `fd ^ dir` |
