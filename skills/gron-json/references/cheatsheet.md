# Cheatsheet: gron-json structured-data queries

One page. Every line replayed from the tomnomnom/gron sources at `88a6234e`.

## Transform

| See | Branch |
|---|---|
| JSON blob | gron into `discrete assignments`, `grep` the lines, read the absolute `path` |
| want JSON back | `gron --ungron` (`-u`), `filtered` lines turn `back into JSON` |
| reverse shortcut | `norg` `alias` (twin `ungron`) in `~/.bashrc`, wraps `gron --ungron` |
| first demo | `README.mkd` line `19`, `fgrep` then `gron --ungron`, `ungron` at `19`, `55`, `57` |

## Flags

| Want | Type |
|---|---|
| only right-hand sides | `gron --values` (`-v`), prints `just the values`, drops the `path` |
| JSON lines input | `gron --stream` (`-s`), each line a `separate JSON` object |
| JSON stream out | `gron --json` (`-j`), a `JSON stream` of path plus value pairs |
| append a key | `withBare` bare word, `withQuotedKey` quoted key string, `withNumericKey` `int` index |

## Errors

| Want | Type |
|---|---|
| broken statements | `Failed to parse` statements, code `5`, `Exit Codes` section |
| broken encode | `Failed to encode` JSON, code `6`, `Exit Codes` section |
| path type | `type statement []token` at line `22`, `statement` from line `14`, 70 lines |
| JSON form | `jsonify` at lines `68` and `69`, receiver on `69` |
| transform phrase | `discrete assignments` at lines `6` and `213`, line `6` names `grep` |

## Prove the pin

| Replay | Prints |
|---|---|
| `rg -n ungron work/gron-json/src/README.mkd` | 13 match lines, first at line `19` with `gron --ungron` |
| `rg -n statement work/gron-json/src/statements.go` | 70 match lines, first at line `14`, type at line `22` |
| `rg -n jsonify work/gron-json/src/statements.go` | 2 match lines, lines `68` and `69` |
| `rg -n "discrete assignments" work/gron-json/src/README.mkd` | 2 match lines, lines `6` and `213` |
