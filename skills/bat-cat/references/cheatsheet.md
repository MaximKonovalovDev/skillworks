# Cheatsheet: bat-cat paged reading

One page. Every line replayed from the sharkdp/bat sources at `d9559c69`.

## Read

| See | Branch |
|---|---|
| what is bat | `cat(1)` clone, `syntax highlighting`, `Git integration`, reads only |
| output too large | `pipes its own output to a pager` (`less`), `--paging=never` for `cat` always |
| piped output plain | `non-interactive terminal`, `drop-in replacement for cat`, `plain file contents` |
| numbers only | `bat -n`, `line numbers`, `-n` controls numbers only |

## Pager

| Want | Type |
|---|---|
| which variable wins | `BAT_PAGER` will `override` `PAGER`, `builtin` is the builtin pager |
| where choice came from | `PagerSource`: `EnvVarBatPager`, `EnvVarPager`, `Config`, `Default` |
| which pagers known | `PagerKind`: `Bat` `Less` `More` `Most` `Builtin` `Unknown` |
| classify a binary | `from_bin`: `less` to `Less`, `builtin` to `Builtin`, self to `Bat` |

## Lines

| Want | Type |
|---|---|
| bat phrase | `syntax highlighting` 9 lines, first at line `6` with `cat(1)` clone |
| numbers demo | `line numbers` 7 lines, line `94` runs `bat -n` |
| pager enum | `Pager` 28 lines, line `6` defines `PagerSource` |
| pager variable | `BAT_PAGER` 7 lines, line `647` sets `builtin` |

## Prove the pin

| Replay | Prints |
|---|---|
| `rg -n "syntax highlighting" work/bat-cat/src/README.md` | 9 match lines, first at line `6` with `cat(1)` clone |
| `rg -n "line numbers" work/bat-cat/src/README.md` | 7 match lines, first at line `94` with `bat -n` |
| `rg -n Pager work/bat-cat/src/pager.rs` | 28 match lines, first at line `6` with `PagerSource` |
| `rg -n BAT_PAGER work/bat-cat/src/README.md` | 7 match lines, first at line `647` with `builtin` |
