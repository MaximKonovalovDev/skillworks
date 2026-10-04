# pilot-109 run log (2026-10-04T21:28-21:45Z, run pilot-view-r5)

Stranger-run against product changes since pilot-108 (2026-10-04T21:25Z):
76a62de reseal (git-one-branch + repo-read-first live-proofs resealed, the
product.token lane trigger) plus 1f46652 pack assets (packs/, not product).
Scratch only (`$env:TEMP\opencode\pilot-109\`); repo product paths untouched
by this run (`git status --short -- book2skill mcp_server tools skills tests`
empty). No code, no commits. Opened every capture (READ SKILL.md + make.json
below).

## Pipeline (scratch skill pilot-109-demo, own-words 485-char 2-doc harbor/beacon source)

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in src --name pilot-109-demo --description ... --qa qa.jsonl --work <scratch>/work --skill <scratch>/pilot-109-demo` (qa in `{"q","must"}` shape, 3 Qs) | 0 | extract 485 chars 2 files, split 1 chunk, index 1 record, eval 3/3 = 1.000, audit 6 files 333 tokens, fill: SKILL.md + 3 files still scaffold, receipt make.json gate pass |
| 2 | READ SKILL.md | — | 357 bytes: frontmatter + "Built from owned sources. Start with ..." (pure scaffold, opened) |
| 3 | `export --skill <scaffold> --target claude --out <scratch>/dist` | 1 | `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text; ...` — holds, no packet |
| 4 | `make ... --target claude --out <scratch>/dist2` (second skill pilot-109-held) | 1 | same hold with files named — holds, no packet |
| 4b | `build --name wrong-name` vs dir `pilot-109-demo` | 2 | `--name 'wrong-name' must match skill dir 'pilot-109-demo'` — rule quoted, correct refusal |
| 4c | `make --name pilot-109-demo` vs dir `wrongdir` | 2 | same rule quoted — correct refusal (earlier EXIT:1 was pipe distortion, clean rerun is 2) |

## Sweeps

| # | command | result |
|---|---|---|
| 5 | `python -m pytest tests/ -q` | 427 passed, 113 skipped (100 s), exit 0 — same as pilot-108, reseal still green |
| 6 | `node sprint/check.mjs` | RESULT PASS 20 pass 0 warn 0 fail |
| 7 | `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks` | RESULT PASS 11 pass 0 warn 0 fail |
| 8 | `python tools/fleet_failures.py scan` | exit 0; top classes with counts + plain-reader text (`163 task: Task cancelled`, `109 edit: Could not find oldString ...`, `109 bash: Tool execution aborted`) — OK, no packet |
| 9 | `python tools/pack_check.py packs/fleet-vol-1` | RESULT PASS 13 checks 0 warnings (cover + demo + screenshots all PASS) — unchanged since pilot-108 |
| 9b | `python tools/pack_check.py <scratch>/badpack` (fail path) | RESULT FAIL `FAIL pack.json: cannot read (.../pack.json)` exit 1 — fail path names why, no packet |

## Filed

- None. No NEW stranger-visible defects. Scaffold no-target make exit 0 is K-54 OWNER (verdict pending, not re-filed); the 357-byte scaffold ships nowhere (direct export + make --target both hold with files named). 76a62de touched only live-proof.json x2 + team/p5.md: proofs, not stranger-visible behavior.

## Guards

- Scratch stayed under `$env:TEMP\opencode\` (pilot-109 only).
- No export with `--out` inside `skills/` (all `--out` pointed at scratch dist/dist2).
- `Get-ChildItem skills -Recurse -Directory -Filter export` → nothing; longest skills path 107 chars.
- `git status --short -- book2skill mcp_server tools skills tests` → empty, no pilot files.
