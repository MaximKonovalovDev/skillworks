# pilot-110 run log (2026-10-05T08:56-09:05Z, run pilot-view-r1)

Stranger-run against product changes since pilot-109 (2026-10-04T21:45Z):
2f0cdba doctor DR-1005-1 (skills/pwsh-for-bash-writers/references/target-class.json
+ evals/pwsh-for-bash-writers_trials.jsonl + board row, the product.token lane
trigger). Scratch only (`$env:TEMP\opencode\pilot-110\`); repo product paths
untouched by this run (all `--work/--skill/--out` pointed at scratch;
`git status` on product paths shows one M held by another seat:
M skills/pwsh-for-bash-writers/references/live-proof.json, not a pilot file).
No code, no commits. Opened every capture (READ SKILL.md + make.json below).

## Pipeline (scratch skill pilot-110-demo, own-words 553-char 2-doc harbor/beacon source)

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in src --name pilot-110-demo --description ... --qa qa.jsonl --work <scratch>/work --skill <scratch>/pilot-110-demo` (qa in `{"q","must"}` shape, 3 Qs) | 0 | extract 553 chars 2 files, split 1 chunk, index 1 record, eval 3/3 = 1.000, audit 6 files 349 tokens, fill: SKILL.md + 3 files still scaffold, receipt make.json gate pass |
| 2 | READ SKILL.md | — | 352 bytes: frontmatter + "Built from owned sources. Start with ..." (pure scaffold, opened) |
| 3 | `export --skill <scaffold> --target claude --out <scratch>/dist` | 1 | `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text; ...` — holds, no packet |
| 4 | `make ... --target claude --out <scratch>/dist2` (second skill pilot-110-held) | 1 | same hold with files named — holds, no packet |
| 4b | `build --name wrong-name` vs dir `pilot-110-demo` | 2 | `--name 'wrong-name' must match skill dir 'pilot-110-demo'` — rule quoted, correct refusal |

## Sweeps

| # | command | result |
|---|---|---|
| 5 | `python -m pytest tests/ -q` | 427 passed, 113 skipped (93 s), exit 0 — same as pilot-108/109 |
| 6 | `node sprint/check.mjs` | RESULT PASS 20 pass 0 warn 0 fail |
| 7 | `node C:/empire/center/arsenal.mjs --check skillworks` | RESULT PASS 11 pass 0 warn 0 fail |
| 8 | `python tools/fleet_failures.py scan` | exit 0; top classes with counts + plain-reader text (`128 task: Task cancelled`, `113 edit: Could not find oldString ...`, `85 bash: Tool execution aborted`) — OK, no packet |
| 9 | `python tools/pack_check.py packs/fleet-vol-1` | RESULT PASS 13 checks 0 warnings (cover + demo + screenshots all PASS) — unchanged since pilot-109 |
| 9b | `python tools/pack_check.py <scratch>/badpack` (fail path) | RESULT FAIL `FAIL pack.json: cannot read (.../pack.json)` exit 1 — fail path names why, no packet |

## Filed

- None. No NEW stranger-visible defects. Scaffold no-target make exit 0 is K-54 OWNER (verdict pending, not re-filed); the 352-byte scaffold ships nowhere (direct export + make --target both hold with files named). 2f0cdba touched only target-class.json + trials + board: doctor-lane proof, not stranger-visible behavior.

## Guards

- Scratch stayed under `$env:TEMP\opencode\` (pilot-110 only).
- No export with `--out` inside `skills/` (all `--out` pointed at scratch dist/dist2).
- `Get-ChildItem skills -Recurse -Directory -Filter export` → nothing; no path over 240 chars.
- `git status --short -- book2skill mcp_server tools skills tests` → only the one live-proof.json M from another seat, no pilot files.
