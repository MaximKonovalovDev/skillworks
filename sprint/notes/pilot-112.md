# pilot-112 run log (2026-10-05T11:49Z+, run pilot-view-r2)

Stranger-run against product changes since pilot-111 (2026-10-05T09:55Z):
6572ac9 (new skill edit-unique, `book2skill/gates.py` +1 line,
`tools/install_fleet_skills.py` +1 skill), 96c18a0 (trials + board row),
c9c63bc (pack reseal: listing.md date + 10 live-proof reseals).
Scratch only (`$env:TEMP\opencode\pilot-112\`); repo product paths
untouched (`git status --short -- book2skill mcp_server tools skills
tests` empty). No code, no commits. Opened every capture (READ SKILL.md
+ make.json + zip diff below).

## Pipeline (scratch skill pilot-112-demo, own-words 381-char harbor/beacon source)

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in src --name pilot-112-demo ... --qa qa.jsonl` with `"must": "green"` (string) | 2 | `--qa ... line 1 must be {"q", "must"} (got keys: must, q)` — keys ARE q+must; real violation is must-not-a-list, never stated. Filed packet pilot-112-qa-shape-message.md |
| 2 | same `make` with `"must": ["green"]` etc (3 Qs, list shape) | 0 | extract 381 chars 1 file, split 1 chunk, index 1 record, eval 3/3 = 1.000, audit 6 files 304 tokens, fill: SKILL.md + 3 files still scaffold, receipt make.json gate pass |
| 3 | READ SKILL.md | — | 346 bytes: frontmatter + "Built from owned sources. Start with ..." (pure scaffold, opened) |
| 4 | `export --skill <scaffold> --target claude --out <scratch>/dist` | 1 | `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text; ...` — holds, no packet |
| 5 | `make ... --target claude --out <scratch>/dist2` (second skill pilot-112-held) | 1 | same hold with files named — holds, no packet |
| 6 | `build --name wrong-name` vs dir `pilot-112-demo` | 2 | `--name 'wrong-name' must match skill dir 'pilot-112-demo'` — rule quoted, correct refusal |

## Sweeps

| # | command | result |
|---|---|---|
| 7 | `python -m pytest tests/ -q` | 434 passed, 116 skipped (44 s), exit 0 — up from pilot-111 427/113 (new edit-unique tests) |
| 8 | `node sprint/check.mjs` | RESULT PASS 20 pass 0 warn 0 fail |
| 9 | `node C:/empire/center/arsenal.mjs --check skillworks` | RESULT PASS 11 pass 0 warn 0 fail |
| 10 | `python tools/fleet_failures.py scan` | exit 0; classes with counts in plain-reader text (`131 task: Task cancelled`, `123 edit: Could not find oldString ...`, `87 bash: Tool execution aborted`, `33 edit: Found multiple matches ...`, `23 read missing: 000-tool-sprint.md`) — OK, no packet (read-missing reflects deleted queue files, environmental) |
| 11 | `python tools/pack_check.py packs/fleet-vol-1` | RESULT FAIL: fleet-vol-1 (2 findings), exit 1 — NEW vs pilot-111 PASS. Filed packet pilot-112-stale-zip.md |
| 12 | `python tools/pack_check.py <scratch>/badpack` (fail path) | RESULT FAIL `FAIL pack.json: cannot read (.../pack.json)` exit 1 — fail path names why, no packet |

## Filed

- pilot-112-stale-zip.md: buyer zip LICENSES.md says "read 2026-10-05", committed pack.json generates "read 2026-10-04"; gate red at clean HEAD, contradicts c9c63bc proof line. Second FAIL (factory JUDGE) is knock-on of the first.
- pilot-112-qa-shape-message.md: string-`must` refusal reports wrong keys when keys are right; never states must-must-be-list.
- Not filed: scaffold no-target make exit 0 stays K-54 OWNER (verdict pending); 346-byte scaffold ships nowhere (both export paths hold).

## Guards

- Scratch stayed under `$env:TEMP\opencode\` (pilot-112 only + cmp script).
- No export with `--out` inside `skills/`.
- `Get-ChildItem skills -Recurse -Directory -Filter export` → nothing; no path over 240 chars under packs/.
- `git status --short -- book2skill mcp_server tools skills tests` → empty, no pilot files.
