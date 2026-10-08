# Cheatsheet: lsd-ls directory listing

One page. Every line replayed from the lsd-rs/lsd sources at `4b6c14a1`.

## Aliases and icons

| See | Branch |
|---|---|
| one-key tree | `lt`, `lsd --tree`, `alias` |
| change all dirs | `filetype`, `name`, `extension` |
| version status | `--git`, `reduction`, `recursively` |
| full metadata | `--long`, `table`, `blocks` |

## Trees sorts config

| Want | Type |
|---|---|
| bound the tree | `--tree`, `--depth`, `recurs` |
| order the rows | `timesort`, `sizesort`, `reverse` |
| trial a theme | `--config-file`, `XDG_CONFIG_HOME`, `.config/lsd` |
| isolate the fault | `--icon never`, `--ignore-config`, `LS_COLORS` |

## Lines

| Want | Type |
|---|---|
| icon claim | `icon` 5 lines, first at line `30` with colours or icons |
| sort claim | `sort` 9 lines, first at line `38` with extensionsort |
| alias claim | `alias` 8 lines, first at line `89` with shell config |
| config claim | `XDG_CONFIG_HOME` 5 lines, first at line `125` with the config path |

## Prove the pin

| Replay | Prints |
|---|---|
| `rg -n "icon" work/lsd-ls/src/lsd.md` | 5 match lines, first at line `30` with icons |
| `rg -n "sort" work/lsd-ls/src/lsd.md` | 9 match lines, first at line `38` with sort |
| `rg -n "alias" work/lsd-ls/src/README.md` | 8 match lines, first at line `89` with alias |
| `rg -n "XDG_CONFIG_HOME" work/lsd-ls/src/lsd.md` | 2 match lines, first at line `173` with the config file |
