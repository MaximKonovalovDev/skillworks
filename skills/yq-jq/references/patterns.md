# Patterns: symptom to branch

Each recipe starts from a structured-data query miss the loop really makes, then names the one branch that fixes it. All replays ran on this PC on 2026-10-07.

## YAML fed straight to a JSON reader

Symptom: the parse throws `Expecting value` on the first mapping line.

- Transcode first: yq loads each `YAML` document and encodes it as `JSON` before `jq` sees it (pair `yq-p01`).
- prints: `transcode PASS yaml-to-json`

## Pipeline prints JSON but the next step needs YAML

Symptom: the downstream step chokes on braces where mappings belong.

- Pass `--yaml-output`/`-y` so jq output converts `back into YAML`; without it the output stays JSON (pair `yq-p02`).
- prints: `yamlout PASS back-into-yaml`

## XML queried with the plain entry point

Symptom: the YAML loader throws on angle brackets.

- Use the `xq` entry point, which sets `input_format` to `xml` (pair `yq-p03`).
- prints: `entry PASS xq-handles-xml`

## TOML queried with the wrong entry point

Symptom: sections in brackets parse as nothing the filter expects.

- Use the `tomlq` entry point, which sets `input_format` to `toml` (pair `yq-p04`).
- prints: `entry PASS tomlq-handles-toml`

## Docs build needs the header only

Symptom: the whole Markdown file, body included, reaches the filter.

- Pass `--yaml-frontmatter`/`-F`: one header document goes to jq with `JSON or YAML output`, the body passes through (pair `yq-p05`).
- prints: `front PASS one-header-doc`

## In-place edit refused at the gate

Symptom: the run exits with `-i/--in-place can only be used with -y/-Y/-t/-T/-x`.

- Add an output flag (`-y`/`-Y`/`-t`/`-T`/`-x`) and pass filename arguments, never stdin (pair `yq-p06`).
- prints: `inplace PASS wrote-with-yaml-output`

## Round-trip tags lost on output

Symptom: `!Ref` and folded styles vanish from the emitted YAML.

- Use `-Y` (`annotated_yaml`), which keeps tags, styles, and comments; plain `-y` drops them (pair `yq-p07`).
- prints: `outputs PASS annotated_yaml-keeps-annotations`

## Pipeline fails with no stage named

Symptom: nobody can tell whether input parsing or jq broke.

- Read the stage: input failures print `Error` at the `reading` stage with the file name; filter failures print `jq produced invalid JSON` (pair `yq-p08`).
- prints: `errors PASS reading-stage-named`
