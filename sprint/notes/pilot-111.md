# pilot-111 run log (2026-10-05T09:42-09:55Z, run pilot-view-r2)

Stranger-run against product changes since pilot-110 (2026-10-05T09:05Z):
d1435ca pack reseal (skills/pwsh-for-bash-writers/references/live-proof.json,
the product.token lane trigger) plus ed0b022 DR-1005-2 and e4b3ae8 DR-1005-3
(skills/*/references/target-class.json + trials + board rows: proof files,
not stranger-visible behavior). Scratch only
(`$env:TEMP\opencode\pilot-111\`); repo product paths untouched by this run
(all `--work/--skill/--out` pointed at scratch; `git status --short --
book2skill mcp_server tools skills tests` empty). No code, no commits.
Opened every capture (READ SKILL.md + make.json below).

## Pipeline (scratch skill pilot-111-demo, own-words 448-char 2-doc harbor/beacon source)

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in src --name pilot-111-demo --description ... --qa qa.jsonl --work <scratch>/work --skill <scratch>/pilot-111-demo` (qa in `{"q","must"}` shape, 3 Qs) | 0 | extract 448 chars 2 files, split 1 chunk, index 1 record, eval 3/3 = 1.000, audit 6 files 320 tokens, fill: SKILL.md + 3 files still scaffold, receipt make.json gate pass |
| 2 | READ SKILL.md | — | 341 bytes: frontmatter + "Built from owned sources. Start with ..." (pure scaffold, opened) |
| 3 | `export --skill <scaffold> --target claude --out <scratch>/dist` | 1 | `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text; ...` — holds, no packet |
| 4 | `make ... --target claude --out <scratch>/dist2` (second skill pilot-111-held) | 1 | same hold with files named — holds, no packet |
| 4b | `build --name wrong-name` vs dir `pilot-111-demo` | 2 | `--name 'wrong-name' must match skill dir 'pilot-111-demo'` — rule quoted, correct refusal |

## Sweeps

| # | command | result |
|---|---|---|
| 5 | `python -m pytest tests/ -q` | 427 passed, 113 skipped (84 s), exit 0 — same as pilot-108/109/110 |
| 6 | `node sprint/check.mjs` | RESULT PASS 20 pass 0 warn 0 fail |
| 7 | `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks` | RESULT PASS 11 pass 0 warn 0 fail |
| 8 | `python tools/fleet_failures.py scan` | exit 0; top classes with counts + plain-reader text (`131 task: Task cancelled`, `118 edit: Could not find oldString ...`, `86 bash: Tool execution aborted`) — OK, no packet |
| 8b | `python tools/fleet_failures.py loads --from 2026-10-03T00:00Z --to 2026-10-04T00:00Z` | exit 0; `0 loads ... across 0 repos: none` — was 12 loads across 6 repos in pilot-108; tool code unchanged since 0217c83 (git log), live opencode.db rotated (2 GB, written today); environmental, not a product defect, not filed (TS-1 DONE/owned) |
| 8c | `python tools/fleet_failures.py loads --from 2026-10-04T00:00Z --to 2026-10-05T00:00Z` | exit 0; `25 loads ... across 7 repos` — loads counting works on the real thing |
| 9 | `python tools/pack_check.py packs/fleet-vol-1` | RESULT PASS 13 checks 0 warnings — unchanged since pilot-109/110 |
| 9b | `python tools/pack_check.py <scratch>/badpack` (fail path) | RESULT FAIL `FAIL pack.json: cannot read (.../pack.json)` exit 1 — fail path names why, no packet |

## Filed

- None. No NEW stranger-visible defects. Scaffold no-target make exit 0 is K-54 OWNER (verdict pending, not re-filed); the 341-byte scaffold ships nowhere (direct export + make --target both hold with files named). d1435ca/ed0b022/e4b3ae8 touched only proofs + listing + board: no behavior change on the stranger path.

## Guards

- Scratch stayed under `$env:TEMP\opencode\` (pilot-111 only).
- No export with `--out` inside `skills/` (all `--out` pointed at scratch dist/dist2).
- `Get-ChildItem skills -Recurse -Directory -Filter export` → nothing; no path over 240 chars.
- `git status --short -- book2skill mcp_server tools skills tests` → empty, no pilot files.
