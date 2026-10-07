# Cheatsheet: yq-jq structured-data queries

One page. Every line replayed from the kislyuk/yq sources at `b04512f9`.

## Transcode

| See | Branch |
|---|---|
| YAML doc | `transcodes` to `JSON`, pipes to `jq` |
| want YAML back | `--yaml-output`/`-y`, `back into YAML` |
| key order | preserved, `database` before `ports` |
| JSON file | valid YAML already, `yq -y .` converts |

## Entry points

| Want | Type |
|---|---|
| YAML docs | `yq`, `input_format` `yaml`, `program_name` `yq` |
| XML docs | `xq`, `input_format` `xml` |
| TOML docs | `tomlq`, `input_format` `toml` |
| defaults | `cli` line `102` |

## Gates

| Want | Type |
|---|---|
| header only | `--yaml-frontmatter`/`-F`, `YAML input`, `JSON or YAML output` |
| edit a file | `-i`/`--in-place` with `-y`/`-Y`/`-t`/`-T`/`-x`, filenames only |
| keep tags | `-Y`, `annotated_yaml` keeps tags styles comments |
| plain YAML out | `-y`, drops `!Ref` |

## Errors

| Want | Type |
|---|---|
| broken input | `Error` at the `reading` stage with the file name |
| bad filter output | `jq produced invalid JSON` with the output format |
| exit codes | forwards the `jq` code, parse errors exit 1 |

## Prove the pin

| Replay | Prints |
|---|---|
| `rg -n input_format work/yq-jq/src/__init__.py` | 12 match lines, default `yaml` at line `102` |
| `rg -n program_name work/yq-jq/src/__init__.py` | 20 match lines, default `yq` at line `102` |
| `rg -n yaml-output work/yq-jq/src/README.rst` | line `26`, short flag `-y` |
| `rg -n "jq wrapper" work/yq-jq/src/README.rst work/yq-jq/src/__init__.py` | 2 files, the `jq wrapper` phrase |
