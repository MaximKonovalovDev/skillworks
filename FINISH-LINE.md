# Finish line: skillworks (2026-10-03)

What "done" means for skillworks, as bars: skills that make the other loops better, and packs people can buy.
`node C:/Users/me/Desktop/center/finish.mjs skillworks` measures every bar; exit 0 means finished.
Maxim's GO 2026-10-03 ("skillworks is for skills getting better over time"); drafted by Claude Code.

The skill doctor's record lives outside this public repo, in `C:/Users/me/.empire/state/skilldoctor/adopted.csv`,
one line per improved skill: `date,repo,skill,status,no_edit_before,no_edit_after` (status: proposed or adopted).
Nothing private from other repos is ever committed here.

## Bars

| ID | Bar | Proof |
|---|---|---|
| S1 | One improved skill adopted by another repo | `lines C:/Users/me/.empire/state/skilldoctor/adopted.csv 1 ,adopted,` |
| S2 | Improved skills adopted in 5 of the 9 repos | `cmd python tools/finish_proof.py s2` |
| S3 | First tested pack for sale, live on a store | `cmd python tools/finish_proof.py s3` |
| S4 | The MCP server answers and lists every skill | `cmd python -m pytest tests/test_mcp_schema.py tests/test_mcp_skills_dir.py -q` |

## Rules

- Work the lowest open bar first. A `todo` proof is the first job: build it, then write the real proof here (center's vision check FAILs until every bar has one).
- Never edit a proof to make it pass. Changing a bar needs Maxim's word.
