# pilot-105 run log (2026-10-04T08:30-09:00Z)

Stranger-run against product changes since the last pilot view:
K-48 slices (build.py NC gate, Gutenberg strip at build time, eval grades
SKILL text), TS-5 pack gate, TS-3 skill trial, engine-builder skill.
Scratch only (`$env:TEMP\opencode\pilot-105\`); repo product paths
(`book2skill/ mcp_server/ tools/ skills/ tests/`) untouched — see
`git status` guard below. Own-words 469 B 2-doc harbor/beacon source.
No code, no commits.

## Pipeline (scratch skill pilot-105-demo)

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in src --name pilot-105-demo --description ... --qa qa.jsonl --work <scratch> --skill <scratch>` (qa in `{"q","must"}` shape, 3 Qs) | 0 | extract 469 chars 2 files, split 1 chunk, index 1 record, eval 3/3 = 1.000, audit 6 files 330 tokens, fill: 4 files still scaffold, receipt make.json gate pass |
| 2 | READ SKILL.md | — | 363 bytes: frontmatter + "Built from owned sources. Start with ..." (pure scaffold) |
| 3 | `export --skill <scaffold> --target claude --out <scratch>/dist` | 0 | zip_files 7; zip's SKILL.md is the same 363-byte placeholder (read back) — DEFECT, filed |
| 4 | `make ... --target claude --out <scratch>/dist` (second skill pilot-105-held) | 1 | `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text; ...` — hold exists only here |

## Sweeps

| # | command | result |
|---|---|---|
| 5 | `python -m pytest tests/ -q` | 333 passed, 107 skipped (59 s) |
| 6 | `node sprint/check.mjs` | 20 pass, 0 warn, 1 FAIL: `board: DONE without a commit SHA: K-48` (Evidence cell is `Nit fixed: vol0 831 B`, no SHA; DONE SHA deba548 lives only in handoff round 105; the line's only hex `7cefd5f` sits in What). NOT filed: check.mjs header says a FAIL is the lead's first packet, the keeper carries it. Handoff 105 claims PASS 20/0/0 on unchanged committed board. |
| 7 | `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks` | RESULT PASS 11/0/0 |
| 8 | `python tools/fleet_failures.py scan` | exit 0; top classes with counts and plain-reader error text (`173 task: Task cancelled`, `98 edit: Could not find oldString ...`, `71 bash: Tool execution aborted`) — OK, no packet |
| 9 | `python tools/pack_check.py packs/fleet-vol-1` | RESULT PASS (10 checks, 3 store-asset NEEDS); stub dir → `FAIL pack.json: cannot read ...` + RESULT FAIL exit 1 — fail path names why, no packet |

## Filed

- `sprint/queue/ready/pilot-105-scaffold-ships.md` (builder): placeholder skill
  ships past make + direct export; only make --target holds it.

## Guards

- Scratch stayed under `$env:TEMP\opencode\` (pilot-105 only).
- No export with `--out` inside `skills/` (all `--out` pointed at scratch dist).
- `Get-ChildItem skills -Recurse -Directory -Filter export` → nothing (see RESULT run).
- `git status --short -- book2skill mcp_server tools skills tests` → empty (see RESULT run).
