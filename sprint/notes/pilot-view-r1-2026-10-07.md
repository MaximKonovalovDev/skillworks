# pilot-view-r1 run log (2026-10-07T07:01Z, product.token 44d72b4b)

Stranger-run against product changes since pilot-view-r1 (2026-10-03T21:00Z):
convergence 44d72b4 (4 S50 skills plus wire), Vol1 upkeep reseals, cure landings.
Scratch only (`%TEMP%\opencode\pilot-115`), own-words 438-char 2-doc harbor/beacon
source plus `{"q","must"}` QA. First `make` without `--work/--skill` wrote into
repo `skills/ work/` by default; removed both dirs after reading (only other
runs' edits remain). Re-ran fully in scratch. No code, no commits.

Pipeline (scratch skill `pilot-115-demo`):

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in <scratch>/src --name pilot-115-demo --description "Use when ..." --qa qa.jsonl --work <scratch>/work --skill <scratch>/skills/pilot-115-demo` | 0 | `extract folder, 438 chars, 2 files / split 1 / index 1 / build ... / eval 3/3 = 1.000 (gate 0.6) / audit 6 files, 314 tokens / fill SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text` |
| 2 | READ `<scratch>/skills/pilot-115-demo/SKILL.md` | - | 330 bytes, `Built from owned sources` scaffold body; no-target make exit 0 with fill hint is the K-54 OWNER authoring flow, not filed |
| 3 | `export --skill <scratch> --target claude --out <scratch>/dist` | 1 | `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text; write them first` names files, holds |
| 4 | `node sprint/check.mjs` | 0 | `RESULT PASS: 20 pass, 0 warn, 0 fail` |
| 5 | `node center/arsenal.mjs --check skillworks` | 0 | `RESULT PASS: 13 pass, 0 warn, 0 fail` |
| 6 | `tools/fleet_failures.py scan` | 0 | top `109 edit: Could not find oldString ...` plus counts, reads like plain language |
| 7 | `tools/fleet_failures.py --db <missing> scan` | 1 | `no opencode.db at ...` clean refusal, no traceback |
| 8 | `tools/pack_check.py packs/fleet-vol-1` | 0 | `RESULT PASS: fleet-vol-1 (13 checks pass, 0 warnings, 0 store assets still needed)` |
| 9 | `tools/pack_check.py packs/mcp-template` | 1 | `FAIL pack.json: cannot read (... pack.json)` plus `RESULT FAIL`, says why |
| 10 | `tools/pack_check.py packs/does-not-exist` | 1 | `RESULT FAIL: packs/does-not-exist is not a folder` |
| 11 | `python -m pytest tests/ -q` | 1 | 1 failed, 721 passed, 198 skipped in 457 s; sole fail `test_c02_gate::test_c02_golden_gate` is the known runner paperwork fail per handoff round 271, not filed (owning run) |

Observation (not filed, no traceback): `scan --db PATH` (flag after subcommand,
as the tool's own help text and arsenal.json show it) exits 2 `unrecognized
arguments`; the working form is global `fleet_failures.py --db PATH scan`.
Usage error, not a crash; noted for the toolsmith.

Filed: none. No NEW stranger-visible defects.
Guards: `Get-ChildItem skills -Recurse -Directory -Filter export` prints
nothing; repo tree unchanged except other runs' claimed work; scratch root
`%TEMP%\opencode\pilot-115` left for inspection (outside repo).
