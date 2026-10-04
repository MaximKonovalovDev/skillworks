# pilot-108 run log (2026-10-04T21:11-21:25Z, run pilot-view-r4)

Stranger-run against product changes since pilot-107 (2026-10-04T20:10Z):
2c3025c gates+reseal (trial-proof excluded from fingerprint, 3 live-proofs
resealed, cron trial proof). Scratch only (`$env:TEMP\opencode\pilot-108\`);
repo product paths untouched by this run (all `--work/--skill/--out` pointed
at scratch; `git status` on product paths shows only other seats' held
uncommitted reseal work: M skills/git-one-branch + repo-read-first
live-proof.json, not pilot files). No code, no commits. Opened every capture
(READ SKILL.md + make.json below).

## Pipeline (scratch skill pilot-108-demo, own-words 650-char 2-doc harbor/beacon source)

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in src --name pilot-108-demo --description ... --qa qa.jsonl --work <scratch>/work --skill <scratch>/pilot-108-demo` (qa in `{"q","must"}` shape, 3 Qs) | 0 | extract 650 chars 2 files, split 1 chunk, index 1 record, eval 3/3 = 1.000, audit 6 files 357 tokens, fill: SKILL.md + 3 files still scaffold, receipt make.json gate pass |
| 1b | same with mismatched `--skill .../skill --name pilot-108-demo` | 2 | `--name 'pilot-108-demo' must match skill dir 'skill'` — rule quoted, correct refusal |
| 2 | READ SKILL.md | — | 339 bytes: frontmatter + "Built from owned sources. Start with ..." (pure scaffold, opened) |
| 3 | `export --skill <scaffold> --target claude --out <scratch>/dist` | 1 | `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text; ...` — holds, no packet |
| 4 | `make ... --target claude --out <scratch>/dist2` (second skill pilot-108-held) | 1 | same hold with files named — holds, no packet |

## Sweeps

| # | command | result |
|---|---|---|
| 5 | `python -m pytest tests/ -q` | 427 passed, 113 skipped (66 s). FIXED vs pilot-107 (2 stale live-proof FAILs gone after 2c3025c reseal); improvement, no packet |
| 6 | `node sprint/check.mjs` | RESULT PASS 20 pass 0 warn 0 fail |
| 7 | `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks` | RESULT PASS 11/0/0 |
| 8 | `python tools/fleet_failures.py scan` | exit 0; top classes with counts + plain-reader text (`180 task: Task cancelled`, `109 edit: Could not find oldString ...`, `109 bash: Tool execution aborted`) — OK, no packet |
| 8b | `python tools/fleet_failures.py loads --from 2026-10-03T00:00Z --to 2026-10-04T00:00Z` | exit 0; `12 loads ... across 6 repos` — TS-1 exact-window still works on the real thing |
| 9 | `python tools/pack_check.py packs/fleet-vol-1` | RESULT PASS 13 checks 0 warnings (cover + demo + screenshots all PASS) — was already PASS in pilot-107; screenshots now present, improvement not a defect, no packet |
| 9b | `python tools/pack_check.py <scratch>/badpack` (fail path) | RESULT FAIL `FAIL pack.json: cannot read (.../pack.json)` exit 1 — fail path names why, no packet |

## Filed

- None. No NEW stranger-visible defects. Scaffold no-target make exit 0 is K-54 OWNER (verdict pending, not re-filed); the 339-byte scaffold ships nowhere (direct export + make --target both hold with files named).

## Guards

- Scratch stayed under `$env:TEMP\opencode\` (pilot-108 only).
- No export with `--out` inside `skills/` (all `--out` pointed at scratch dist/dist2).
- `Get-ChildItem skills -Recurse -Directory -Filter export` → nothing; longest skills path 107 chars.
- `git status --short -- book2skill mcp_server tools skills tests` → only the two reseal Ms from 2c3025c, no pilot files.
