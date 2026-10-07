---
name: gron-json
description: Use when grepping JSON with gron: discrete assignments, grep plus ungron round-trip, the norg alias, values stream json flags, path builders, and staged exit codes with the exact lines to check.
version: 0.1.0
author: skillworks
license: MIT
---

# Query JSON with gron, the greppable transform

Rules distilled from tomnomnom/gron at `88a6234e` (main, read 2026-10-07) for the structured-data query class: how gron flattens JSON before grep sees it, which flag reverses the operation, which alias shortens it, which flags trim the output, and which gates reject bad invocations. Each rule names the exact token to branch on and the pair that replays it. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`. The runnable proof of every rule is `references/pairs.md` (machine list `references/pairs.json`), replayed by `scripts/run_gron.py`.

## Gron first, then grep

- gron `transforms` each `JSON` document into `discrete assignments`: never feed a raw blob to `grep`, gron first so each line shows the absolute `path` to its value [src: references/pairs.md#gr-p01]
- Pipe assignments through `gron --ungron` (`-u`) to turn the `filtered` lines `back into JSON`: without it the pipeline stays assignment text, never valid JSON [src: references/pairs.md#gr-p02]
- Shorten the reverse step with the `norg` `alias` for `gron --ungron` (twin spelling `ungron`): put the alias line in `~/.bashrc`, each alias wraps `gron --ungron` [src: references/pairs.md#gr-p03]
- Line `19` of `README.mkd` pipes `fgrep "commit.author"` into `gron --ungron`: read the reverse flag there, where `ungron` appears 13 times starting at lines `19`, `55`, and `57` [src: references/pairs.md#gr-p09]

## Flags that trim the output

- Pass `gron --values` (`-v`) to print `just the values` of provided assignments: it drops the `path` and prints only the right-hand sides [src: references/pairs.md#gr-p04]
- Pass `gron --stream` (`-s`) when input is JSON lines: it treats each line as a `separate JSON` object, and one big document parse breaks without it [src: references/pairs.md#gr-p05]
- Pass `gron --json` (`-j`) to represent gron data as a `JSON stream`: each emitted pair carries the path array plus the value [src: references/pairs.md#gr-p06]
- Append keys with the three `statement` builders: `withBare` takes a bare word, `withQuotedKey` takes a quoted key string, `withNumericKey` takes an `int` index [src: references/pairs.md#gr-p07]

## Paths and staged errors

- Line `22` defines `type statement []token`: the `statement` word appears 70 times, the first three at lines `14`, `15`, and `22` [src: references/pairs.md#gr-p10]
- Line `69` defines `func (s statement) jsonify`: the `jsonify` word appears twice at lines `68` and `69`, where `68` documents the conversion [src: references/pairs.md#gr-p11]
- Line `6` says gron makes blobs easier to `grep`: the `discrete assignments` phrase appears twice, at lines `6` and `213` [src: references/pairs.md#gr-p12]
- Read a failure by stage in the `Exit Codes` section: `Failed to parse` statements is code `5`, `Failed to encode` JSON is code `6` [src: references/pairs.md#gr-p08]

## Prove the pin

Replayed live 2026-10-07 with the installed `rg` (each replay ends exit 0):

```
rg -n ungron work/gron-json/src/README.mkd
```

prints 13 match lines, the first three at lines 19, 55, and `57`, where line `19` pipes fgrep into `gron --ungron`. `rg -n statement work/gron-json/src/statements.go` prints 70 match lines starting at lines 14, 15, and `22`, where line `22` defines `type statement []token`. `rg -n jsonify work/gron-json/src/statements.go` prints 2 match lines: lines `68` and `69`, where line `69` defines the `jsonify` receiver. `rg -n "discrete assignments" work/gron-json/src/README.mkd` prints 2 match lines: lines `6` and `213`, where line `6` says gron makes blobs easier to `grep`.
