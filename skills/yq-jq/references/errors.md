# Error lines the pairs replay (all thrown live by scripts/run_yq.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the fixed-query report instead.

- `Expecting value`: fed YAML straight to a JSON reader with no transcode. Pair `yq-p01`
- `no conversion`: pipeline printed JSON where the next step needs YAML. Pair `yq-p02`
- `reads YAML input`: queried XML with the plain yq entry point. Pair `yq-p03`
- `reads TOML input`: queried XML with the tomlq entry point. Pair `yq-p04`
- `frontmatter needs YAML`: sent an XML file with --yaml-frontmatter. Pair `yq-p05`
- `in-place can only be used`: tried -i with plain JSON output and no output flag. Pair `yq-p06`
- `keeps nothing`: asked for an annotated round-trip on plain json out. Pair `yq-p07`
- `ParserError`: parsed a broken YAML document. Pair `yq-p08`
- `missed input_format`: queried config.yml for the entry-point setting. Pair `yq-p09`
- `missed program_name`: queried feed.xml for the program setting. Pair `yq-p10`
- `missed yaml-output`: queried app.toml for the output flag. Pair `yq-p11`
- `missed jq wrapper`: queried app.toml for the wrapper phrase. Pair `yq-p12`
