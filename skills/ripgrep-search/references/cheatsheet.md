# Cheatsheet: ripgrep search precision

One page. Every line replayed or listed from the guide at `3fce3b5b`.

## Pattern kind

| Want | Type |
|---|---|
| literal text | `rg -F 'fn write('` |
| one mark literal, rest regex | `rg -n "fn write\("` |
| case-insensitive | `rg -i fast` |
| case decides itself | `rg -S fast` |
| whole words | `rg -w -e -2` |

## Scope

| Want | Type |
|---|---|
| whole tree (default) | `rg foo` (= `rg foo ./`) |
| one directory | `rg 'fn write\(' src` |
| count, not lines | `rg -c pattern` |
| files that would be searched | `rg --files` |
| stable order | `rg --sort path` |
| surrounding lines | `rg -C 3 pattern` |

## Skips and reversals

| Skip | Reverse |
|---|---|
| ignore files | `rg --no-ignore` |
| hidden files | `rg --hidden` |
| binary (`NUL` byte) | `rg --text` |
| symlinks | `rg --follow` |
| ladder | `rg -u`, `rg -uu`, `rg -uuu` |
| still perplexed | `rg --debug` |

## Narrowing

| Want | Type |
|---|---|
| only TOML | `rg lexopt -g '*.toml'` |
| everything but TOML | `rg lexopt -g '!*.toml'` |
| order matters | later `-g` overrides earlier |
| list types | `rg --type-list` |
| include / exclude type | `rg -t rust` / `rg -T rust` |
| ad-hoc type (one command) | `rg --type-add 'web:*.{html,css,js}' -tweb title` |
| every known type | `rg --type all` |
| inverse of that | `rg --type-not all` |

## Config file

| Step | Value |
|---|---|
| point at it | `RIPGREP_CONFIG_PATH` |
| one line | one shell argument, verbatim |
| comment | `#` starts it |
| valued flag | `--max-columns=150` (or two lines, never `--flag value` on one) |
| one-run override | append flags on the command line |
| opt out | `rg --no-config` |

## Special searches

| Want | Type |
|---|---|
| Latin-1 / other encoding | `rg --encoding` |
| compressed files | `rg --search-zip` |
| cross-line match | `rg --multiline` |
| lookaround / backrefs | `rg --pcre2` (slower) |
| preview a swap | `rg fast README.md -r FAST` |
| real file edit | `rg foo --files-with-matches \| xargs sed` |
