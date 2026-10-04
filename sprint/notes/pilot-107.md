# pilot-107 run log (2026-10-04T19:55-20:10Z, run pilot-view-r2)

Stranger-run against product changes since pilot-106 (2026-10-04T17:05Z):
TS-1 repair 0217c83 (fleet_failures loads exact-window), auto-backup 98a7aad
(rust-book skill, O-033 listing), builder-pack-r2 repair (screenshots, demo).
Scratch only (`$env:TEMP\opencode\pilot-107\`); repo product paths untouched
by this run (all `--work/--skill/--out` pointed at scratch; `git status` on
product paths empty before and after). No code, no commits. Opened every
capture (READ SKILL.md + make.json below).

## Pipeline (scratch skill pilot-107-demo, own-words 436-char 2-doc harbor/beacon source)

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in src --name pilot-107-demo --description ... --qa qa.jsonl --work <scratch> --skill <scratch>` (qa in `{"q","must"}` shape, 3 Qs) | 0 | extract 436 chars 2 files, split 1 chunk, index 1 record, eval 3/3 = 1.000, audit 6 files 317 tokens, fill: SKILL.md + 3 files still scaffold, receipt make.json gate pass |
| 1b | same with `--skill <scratch>/skill` (dir != name) | 2 | `--name 'pilot-107-demo' must match skill dir 'skill'` — rule quoted, correct refusal |
| 2 | READ SKILL.md | — | 343 bytes: frontmatter + "Built from owned sources. Start with ..." (pure scaffold, opened) |
| 3 | `export --skill <scaffold> --target claude --out <scratch>/dist` | 1 | `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text; ...` — holds, no packet |
| 4 | `make ... --target claude --out <scratch>/dist2` (second skill pilot-107-held) | 1 | same hold with files named — holds, no packet |

## Sweeps

| # | command | result |
|---|---|---|
| 5 | `python -m pytest tests/ -q` | 2 failed (test_fleet_skills stale live-proof: git-one-branch, repo-read-first; message quotes the re-run rule, not a traceback), 425 passed, 113 skipped (71 s). NOT filed: both skills are open cure/doctor rows (DR-1004-7, DR-1004-3; handoff 149 lists them as blockers) — owned in-flight, no duplicate packet |
| 6 | `node sprint/check.mjs` | RESULT PASS 20 pass 0 warn 0 fail |
| 7 | `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks` | RESULT PASS 11/0/0 |
| 8 | `python tools/fleet_failures.py scan` | exit 0; top classes with counts + plain-reader text (`183 task: Task cancelled`, `108 edit: Could not find oldString ...`, `103 bash: Tool execution aborted`) — OK, no packet |
| 8b | `python tools/fleet_failures.py loads --from 2026-10-03T00:00Z --to 2026-10-04T00:00Z` | exit 0; `12 loads ... across 6 repos` — TS-1 exact-window works on the real thing |
| 9 | `python tools/pack_check.py packs/fleet-vol-1` | RESULT PASS 13 checks 0 warnings — was FAIL 3 in pilot-106 (demo, screenshots, JUDGE); the pack repair landed, improvement not a defect, no packet |

## Filed

- None. No NEW stranger-visible defects. Scaffold no-target make exit 0 is K-54 OWNER (verdict pending, not re-filed); stale live-proofs are owned DR rows (not re-filed).

## Guards

- Scratch stayed under `$env:TEMP\opencode\` (pilot-107 only).
- No export with `--out` inside `skills/` (all `--out` pointed at scratch dist/dist2).
- `Get-ChildItem skills -Recurse -Directory -Filter export` → nothing.
- `git status --short -- book2skill mcp_server tools skills tests` → empty before and after.
