# pilot-114 run log (2026-10-06T10:40Z+, run pilot-view-r2)

Stranger-run against product changes since pilot-112 (2026-10-05T11:49Z, my
last r2 run): 40781fa (qa-shape fix), 7588cf7 (cargo-book skill +
`book2skill/gates.py`), e1cd02f (`book2skill/split_chapters.py`), da31a0e
(bevy-rust-ecs 0.2.0), 670d4ef/0a28b0c/ef8334e (live-proof reseals),
5bfefa7 (fetch-github-first red test), 11b7858 (pwsh-docs skill), 2f6f3c0
(fetch-github-first skill, judge PASS). Pilot-113 (r1) already covered up
to 5bfefa7; this run covers 11b7858 + 2f6f3c0 on top. Scratch only
(`$env:TEMP\opencode\pilot-114\` with --work/--skill/--out overrides);
repo product paths untouched by this run. No code, no commits. Opened
every capture (READ SKILL.md + make.json + test + sources + proof below).

## Pipeline (scratch skill pilot-114-demo, own-words 678-char harbor/beacon source)

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in src --name pilot-114-demo ... --qa qa.jsonl` with `{"q","must"}` lists (3 Qs) + `--work/--skill` scratch | 0 | extract 678 chars 2 files, split 1 chunk, index 1 record, eval 3/3 = 1.000, audit 6 files 356 tokens, fill: SKILL.md + 3 files still scaffold, receipt make.json gate pass |
| 2 | READ SKILL.md | — | 12 lines: frontmatter + "Built from owned sources. Start with ..." (pure scaffold, opened) |
| 3 | `export --skill <scratch> --target claude --out <scratch>/dist` | 1 | `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text; ...` — holds, no packet |
| 4 | `make ... --target claude --out <scratch>/dist2` (second skill pilot-114-held) | 1 | same hold with files named — holds, no packet |
| 5 | `make` with string-`"must"` qa-bad.jsonl | 2 | `"must" must be a list of words (got str)` — pilot-112 packet FIXED, no packet |
| 6 | `build --name wrong-name` vs dir `pilot-114-demo` | 2 | `--name 'wrong-name' must match skill dir 'pilot-114-demo'` — rule quoted, correct refusal |

## Sweeps

| # | command | result |
|---|---|---|
| 7 | `python -m pytest tests/ -q` | 3 failed, 583 passed, 143 skipped (181 s) — NEW RED vs pilot-113 579/140 green. All 3 in fetch-github-first (DR-1006-1, committed 2f6f3c0). Filed packet pilot-114-fetch-red.md |
| 8 | `node sprint/check.mjs` | RESULT PASS 20 pass 0 warn 0 fail |
| 9 | `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks` | RESULT PASS 13 pass 0 warn 0 fail |
| 10 | `python tools/fleet_failures.py scan` | exit 0; classes with counts in plain-reader text (`110 edit: Could not find oldString ...`, `85 task: Task cancelled`, `82 websearch: StatusCode ...`, `72 bash: Tool execution aborted`, `66 bash: Unknown: ChildProcess.kill ...`) — OK, no packet |
| 11 | `python tools/pack_check.py packs/fleet-vol-1` | RESULT PASS 13/0/0, exit 0 — holds, no packet |
| 12 | `python tools/pack_check.py <scratch>/badpack` (fail path) | RESULT FAIL `FAIL pack.json: cannot read (.../pack.json)` exit 1 — fail path names why, no packet |

## Filed

- pilot-114-fetch-red.md: `pytest` red at clean HEAD after DR-1006-1 — (a) `test_pairs_md_is_current` crashes FileNotFoundError (`pairs_to_md.py` not in HEAD, `git ls-tree` shows only `run_fetch.py`, sibling skills ship both); (b) `test_fleet_skill_sources_and_notices[fetch-github-first]` needs `cli/cli (MIT)` with closing paren, HEAD notices has no fetch line at all and the working-tree line writes `(MIT,` with a comma; (c) `test_fleet_skill_matches_its_last_live_proof` fingerprint `498493b1...` vs current `fcccb3cb...` — ignored `eval_report.json` on disk is hashed into the fingerprint, so any eval run invalidates the proof.
- Not filed: scaffold no-target make exit 0 stays K-54 OWNER (verdict pending); scaffold ships nowhere (both export paths hold).

## Working-tree note (honesty)

`git status --short -- book2skill mcp_server tools skills tests` was NOT empty:
`M skills/task-scope/*` (6 files, DR-1006-2 in progress) plus the
THIRD_PARTY_NOTICES.md working-tree credit lines. All three fetch failures
reproduce at clean HEAD (`git show HEAD:...` / `git ls-tree HEAD` checks in
the packet), so they are product defects, not dirt from the in-progress
round. This run wrote nothing under `skills/`, `work/`, or `book2skill/`.

## Guards

- Scratch stayed under `$env:TEMP\opencode\` (pilot-114 only).
- No export with `--out` inside `skills/` (all `--out` pointed at scratch dist/dist2/badpack).
- `Get-ChildItem skills -Recurse -Directory -Filter export` → nothing (checked below); no path over 240 chars under packs/.
- `git status --short -- book2skill mcp_server tools skills tests work` shows only the pre-existing round dirt above, no pilot files.
