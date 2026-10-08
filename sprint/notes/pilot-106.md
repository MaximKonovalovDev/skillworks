# pilot-106 run log (2026-10-04T16:54-17:05Z, run pilot-view-r1)

Stranger-run against product changes since pilot-105 (2026-10-04T09:00Z):
cure re-seal 4b2b262 (product.token), doctor DR-1004-9 39da4fa, scaffold
fb1c529, plus open cure/doctor edits. Scratch only
(`$env:TEMP\opencode\pilot-106\`); repo product paths untouched by this
run (all `--work/--skill/--out` pointed at scratch; `git status` on
product paths shows only other seats' held uncommitted work per handoff
round 139: engine-builder + real-browser-automation live-proofs,
repo-read-first trial-proof, untracked rust-book + task-scope). No code,
no commits. Opened every capture (READ SKILL.md + make.json below).

## Pipeline (scratch skill pilot-106-demo, own-words 464-char 2-doc harbor/beacon source)

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in src --name pilot-106-demo --description ... --qa qa.jsonl --work <scratch> --skill <scratch>` (qa in `{"q","must"}` shape, 3 Qs) | 0 | extract 464 chars 2 files, split 1 chunk, index 1 record, eval 3/3 = 1.000, audit 6 files 324 tokens, fill: SKILL.md + 3 files still scaffold, receipt make.json gate pass |
| 2 | READ SKILL.md | — | 343 bytes: frontmatter + "Built from owned sources. Start with ..." (pure scaffold, opened) |
| 3 | `export --skill <scaffold> --target claude --out <scratch>/dist` | 1 | `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text; ...` — FIXED vs pilot-105 (which shipped the placeholder at exit 0); matches K-54 builder verification abfc4e2, no packet |
| 4 | `make ... --target claude --out <scratch>/dist2` (second skill pilot-106-held) | 1 | same hold with files named — holds, no packet |

## Sweeps

| # | command | result |
|---|---|---|
| 5 | `python -m pytest tests/ -q` | 2 failed (test_fleet_skills stale live-proof: git-one-branch since 2026-10-03T18:55Z, repo-read-first since 2026-10-04T12:44Z; message quotes the re-run rule, not a traceback), 424 passed, 113 skipped (91 s). NOT filed: both skills are open cure/doctor rows (DR-1004-7 git-one-branch, DR-1004-3 repo-read-first; handoff 139 lists their proofs as held uncommitted) — owned in-flight, no duplicate packet |
| 6 | `node sprint/check.mjs` | RESULT PASS 20 pass 0 warn 0 fail (pilot-105's K-48 DONE-without-SHA FAIL is gone) |
| 7 | `node C:/empire/center/arsenal.mjs --check skillworks` | RESULT PASS 11/0/0 |
| 8 | `python tools/fleet_failures.py scan` | exit 0; top classes with counts + plain-reader text (`186 task: Task cancelled`, `102 edit: Could not find oldString ...`, `100 bash: Tool execution aborted`) — OK, no packet |
| 9 | `python tools/pack_check.py packs/fleet-vol-1` | RESULT FAIL 3 findings, each naming why (demo GIF, three 1280x800 screenshots, factory JUDGE.md) — fail path names why, no packet |

## Filed

- None. No NEW stranger-visible defects. Scaffold no-target make exit 0 is K-54 OWNER (verdict pending, not re-filed); stale live-proofs are owned DR rows (not re-filed).

## Guards

- Scratch stayed under `$env:TEMP\opencode\` (pilot-106 only).
- No export with `--out` inside `skills/` (all `--out` pointed at scratch dist/dist2).
- `Get-ChildItem skills -Recurse -Directory -Filter export` → nothing; longest skills path 107 chars.
