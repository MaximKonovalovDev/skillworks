# pilot-115 run log (2026-10-06T12:23Z+, run pilot-view-r3)

Stranger-run against product changes since pilot-114 (my last r2 run covered
up to 2f6f3c0): d9e06fb (task-scope v1.1.0) + a8b4cfe (pilot-114 fetch-red
fix, the product.token commit). Scratch only
(`$env:TEMP\opencode\pilot-115\` with --work/--skill/--out overrides);
repo product paths untouched by this run. No code, no commits. Opened
every capture (READ SKILL.md + make.json below).

## Pipeline (scratch skill pilot-115-demo, own-words 495-char harbor/beacon source)

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in src --name pilot-115-demo ... --qa qa.jsonl` with `{"q","must"}` lists (3 Qs) + scratch --work/--skill | 0 | extract 495 chars 2 files, split 1 chunk, index 1 record, eval 3/3 = 1.000, audit 6 files 332 tokens, fill: SKILL.md + 3 files still scaffold, receipt make.json gate pass |
| 2 | READ SKILL.md | — | 12 lines, 347 bytes: frontmatter + "Built from owned sources. ..." (pure scaffold, opened) |
| 3 | `export --skill <scratch> --target claude --out <scratch>/dist` | 1 | `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text; ...` — holds, no packet |
| 4 | `make ... --target claude --out <scratch>/dist2` (second skill pilot-115-held) | 1 | same hold with files named — holds, no packet |
| 5 | `make` with string-`"must"` qa-bad.jsonl | 2 | `"must" must be a list of words (got str)` — pilot-112 packet still fixed, no packet |
| 6 | `build --name wrong-name` vs dir `pilot-115-demo` | 2 | `--name 'wrong-name' must match skill dir 'pilot-115-demo'` — rule quoted, correct refusal |

Scaffold no-target make exit 0 stays K-54 OWNER (verdict pending); scaffold
ships nowhere (both export paths hold). No packet per K-54.

## Sweeps

| # | command | result |
|---|---|---|
| 7 | `python -m pytest tests/ -q` | 1 failed, 585 passed, 143 skipped (72 s). ONLY failure: `test_seat_guard::test_real_skills_tree_has_no_untracked_files` flags 5 untracked files under `skills/playwright-docs/` — the concurrent builder-book-r3 run (claimed BK-1006-2 12:23Z, same minute) mid-build, not clean-HEAD product. Round 220 handoff reports 586 green on a clean tree; 585+1=586 matches. No packet (round dirt, cf. pilot-114 honesty note) |
| 8 | fetch-red re-proof (pilot-114's 3 reds vs a8b4cfe) | `tests/test_fetch_github_first.py` 3 passed 3 skipped; `-k "pairs_md or live_proof and fetch"` 16 passed; gate needle `cli/cli (MIT)` with paren restored at `book2skill/gates.py:61` — all 3 reds FIXED, no packet |
| 9 | `node sprint/check.mjs` | RESULT PASS 20 pass 0 warn 0 fail |
| 10 | `node C:/empire/center/arsenal.mjs --check skillworks` | RESULT PASS 13 pass 0 warn 0 fail (every arsenal tool's test) |
| 11 | `python tools/fleet_failures.py scan` | exit 0; classes with counts in plain-reader text (`123 edit: Could not find oldString ...`, `83 task: Task cancelled`, `82 websearch: StatusCode ...`, `73 bash: Tool execution aborted`, `66 bash: Unknown: ChildProcess.kill ...`) — OK, no packet |
| 12 | `python tools/pack_check.py packs/fleet-vol-1` | RESULT PASS 13/0/0, exit 0 — holds, no packet |
| 13 | `python tools/pack_check.py <scratch>/badpack` (fail path) | RESULT FAIL `FAIL pack.json: cannot read (.../pack.json)` exit 1 — fail path names why, no packet |

## Filed

None. No defect found at clean HEAD; the one red is another seat's live
working tree. No packet per "no defect, no packet".

## Guards

- Scratch stayed under `$env:TEMP\opencode\` (pilot-115 only); scratch root removed after run.
- No export with `--out` inside `skills/` (all `--out` pointed at scratch dist/dist2/badpack).
- `Get-ChildItem skills -Recurse -Directory -Filter export` → nothing; no pilot path over 240 chars.
- `git status --short -- book2skill mcp_server tools skills tests` shows only others' round dirt (`M skills/task-scope/*` DR-1006-2, `?? skills/playwright-docs/` BK-1006-2), no pilot files.
