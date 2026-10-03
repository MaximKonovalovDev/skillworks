# Finish line: skillworks (2026-10-03, bars rewritten 2026-10-04)

What "done" means for skillworks, as bars: skills that make the other loops better, and packs people can buy.
`node C:/Users/me/Desktop/center/finish.mjs skillworks` measures every bar; exit 0 means finished.
Maxim's GO 2026-10-03 ("skillworks is for skills getting better over time"); drafted by Claude Code.
Maxim's YES 2026-10-04: S1 and S2 counted installs and were met on day one, so they now count real loads; S5 and S6 added.

The skill doctor's record lives outside this public repo, in `C:/Users/me/.empire/state/skilldoctor/adopted.csv`,
one line per installed skill: `date,repo,skill,status,before,after` (status: proposed or adopted; before and
after are the failure class counts of the 48 h before and the 48 h after the install).
Nothing private from other repos is ever committed here.

## Bars

| ID | Bar | Proof |
|---|---|---|
| S1 | Skills of this repo are really used: 10 loads in 24 h by loops outside skillworks | `cmd python tools/finish_proof.py s1` |
| S2 | Those loads come from 5 of the other 8 repos in the same 24 h | `cmd python tools/finish_proof.py s2` |
| S3 | First tested pack for sale (Fleet Vol 1), live on a store | `cmd python tools/finish_proof.py s3` |
| S4 | The MCP server answers and lists every skill | `cmd python -m pytest tests/test_mcp_schema.py tests/test_mcp_skills_dir.py -q` |
| S5 | A failure class fell by half in the 48 h after a skill was installed | `cmd python tools/finish_proof.py s5` |
| S6 | 8 skills proven (a current live proof, or a trial of 10 runs with lift 0.3) | `cmd python tools/finish_proof.py s6` |

## Rules

- Work the lowest open bar first. A `todo` proof is the first job: build it, then write the real proof here (center's vision check FAILs until every bar has one).
- Never edit a proof to make it pass. Changing a bar needs Maxim's word.
- S1 and S2 read the OpenCode history read-only: a `skill` call that names a skill of this repo, in a session of another repo. An install row in `adopted.csv` is not a load.
