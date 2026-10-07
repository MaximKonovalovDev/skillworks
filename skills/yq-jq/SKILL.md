---
name: yq-jq
description: Use when querying YAML, XML, or TOML with yq: YAML-to-JSON transcode, the -y/-Y output flags, xq and tomlq entry points, frontmatter and in-place gates, and staged errors with the exact lines to check.
version: 0.1.0
author: skillworks
license: MIT
---

# Query structured data with yq, the jq wrapper

Rules distilled from kislyuk/yq at `b04512f9` (main, pushed 2026-09-27) for the structured-data query class: how yq transcodes each input before jq sees it, which flag converts output back, which entry point reads which format, and which gates reject bad invocations. Each rule names the exact token to branch on and the pair that replays it. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`. The runnable proof of every rule is `references/pairs.md` (machine list `references/pairs.json`), replayed by `scripts/run_yq.py`.

## Transcode first, then filter

- yq `transcodes` each `YAML` document to `JSON` and pipes it to `jq`: never feed a YAML file to a JSON reader, transcode first [src: references/pairs.md#yq-p01]
- By default no conversion of `jq` output is done: pass `--yaml-output`/`-y` to convert it `back into YAML`, and use `yq -y .` to turn JSON into YAML since YAML treats JSON as its dialect [src: references/pairs.md#yq-p02]
- Mapping key order is preserved on the round trip: expect `database` before `ports` after a `-y` pass, never a re-sorted mapping [src: references/pairs.md#yq-p02]
- Query XML with the `xq` entry point, which sets `input_format` to `xml` and transcodes via xmltodict; the plain `yq` entry point reads YAML input [src: references/pairs.md#yq-p03]
- Query TOML with the `tomlq` entry point, which sets `input_format` to `toml` and transcodes via tomlkit; it reads TOML input [src: references/pairs.md#yq-p04]
- The `cli` default on line `102` sets `input_format` to `yaml` with `program_name` `yq`; `xq` and `tomlq` override both values [src: references/pairs.md#yq-p09]
- yq is a `jq wrapper` for YAML documents (`README.rst` line 1): it never filters YAML itself, it pipes transcoded JSON to `jq` [src: references/pairs.md#yq-p12]
- The `-y` short flag is documented on line `26` of `README.rst`: read the flag there, never in the implementation file [src: references/pairs.md#yq-p11]
- The running tool travels as `program_name`: `yq` by default, `xq` or `tomlq` when those entry points run [src: references/pairs.md#yq-p10]

## Frontmatter and in-place gates

- Process a Markdown header with `--yaml-frontmatter`/`-F`: only the first document goes to jq as `YAML input` with `JSON or YAML output`, and the closing delimiter plus body pass through unchanged [src: references/pairs.md#yq-p05]
- A header without a closing delimiter is processed as ordinary YAML: never assume `-F` split a file that has no closing marker [src: references/pairs.md#yq-p05]
- Edit files with `-i`/`--in-place` only alongside an output flag: `-y`/`-Y` plus `-t`/`-T` plus `-x` pass the gate, while plain output exits with `-i/--in-place can only be used with -y/-Y/-t/-T/-x` [src: references/pairs.md#yq-p06]
- `--in-place` needs filename arguments: it refuses standard input, and each invocation takes one input file (or several only with `--in-place`) [src: references/pairs.md#yq-p06]

## Outputs and staged errors

- Pick `output_format` per need: `json` by default, `yaml` via `-y`, `annotated_yaml` via `-Y` which keeps tags, styles, and comments; `toml`, `annotated_toml`, and `xml` serve the other entry points [src: references/pairs.md#yq-p07]
- Plain `-y` drops custom tags such as `!Ref` and folded styles: use `-Y` to re-apply them from the carried metadata [src: references/pairs.md#yq-p07]
- Check `-Y` filters for compatibility first: injected metadata turns a 2-entry array into 4 entries, so a counting filter must expect the extra items [src: references/pairs.md#yq-p07]
- Read a failure by stage: a broken document prints `Error` naming the `reading` stage with the input name, while bad filter output prints `jq produced invalid JSON` naming the output format [src: references/pairs.md#yq-p08]
- yq forwards the exit code `jq` produced: a YAML parse error exits 1, and a missing `jq` binary prints `Error starting jq` with the install hint [src: references/pairs.md#yq-p08]

## Prove the pin

Replayed live 2026-10-07 with the installed `rg` (each replay ends exit 0):

```
rg -n input_format work/yq-jq/src/__init__.py
```

prints 12 match lines, the first three at lines 95, 99, and `102`, where line `102` sets the default `input_format` to `yaml`. `rg -n program_name work/yq-jq/src/__init__.py` prints 20 match lines starting at lines 95, 99, and `102`, where line `102` sets the default `program_name` to `yq`. `rg -n yaml-output work/yq-jq/src/README.rst` prints 1 match line: line `26`, which documents `--yaml-output` with its short flag `-y`. `rg -n "jq wrapper" work/yq-jq/src/README.rst work/yq-jq/src/__init__.py` prints 2 match lines: `README.rst` line 1 and `__init__.py` line 2, both carrying the `jq wrapper` phrase.
