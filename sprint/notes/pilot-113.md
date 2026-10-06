# pilot-113 run log (2026-10-06T09:26Z+, run pilot-view-r1)

Stranger-run against product changes since pilot-112 (2026-10-05T11:49Z):
7588cf7 (cargo-book skill + `book2skill/gates.py`), e1cd02f
(`book2skill/split_chapters.py`), da31a0e (bevy-rust-ecs 0.2.0),
670d4ef/0a28b0c/8c13f1c/ef8334e (live-proof reseals), 5bfefa7
(fetch-github-first target-class). Scratch only
(`$env:TEMP\opencode\pilot-113\` with --work/--skill overrides after one
accidental default-path make was removed); repo product paths untouched
(`git status --short -- book2skill mcp_server tools skills tests work`
empty). No code, no commits. Opened every capture (READ SKILL.md + outputs
below).

## Pipeline (scratch skill pilot-113-demo, own-words 382-char harbor/beacon source)

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in src --name pilot-113-demo ... --qa qa.jsonl` with `{"q","must"}` lists (3 Qs) + `--work/--skill` scratch | 0 | extract 416 chars 2 files, split 1 chunk, index 1 record, eval 3/3 = 1.000, audit 6 files 311 tokens, fill: SKILL.md + 3 files still scaffold, receipt make.json gate pass |
| 2 | READ SKILL.md | — | 336 bytes: frontmatter + "Built from owned sources. Start with ..." (pure scaffold, opened) |
| 3 | `export --skill <scratch> --target claude --out <scratch>/dist` | 1 | `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text; ...` — holds, no packet |
| 4 | `make ... --target claude --out <scratch>/dist2` (second skill pilot-113-held) | 1 | same hold with files named — holds, no packet |
| 5 | `make` with string-`"must"` qa-bad.jsonl | 2 | `"must" must be a list of words (got str)` — pilot-112 packet FIXED (old wrong-keys message gone), no packet |
| 6 | `build --name wrong-name` vs dir `pilot-113-demo` | 2 | `--name 'wrong-name' must match skill dir 'pilot-113-demo'` — rule quoted, correct refusal |

## Sweeps

| # | command | result |
|---|---|---|
| 7 | `python -m pytest tests/ -q` | 579 passed, 140 skipped (97 s), exit 0 — up from pilot-112 434/116 (BK-1005-2 repair suite) |
| 8 | `node sprint/check.mjs` | RESULT PASS 20 pass 0 warn 0 fail |
| 9 | `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks` | RESULT PASS 13 pass 0 warn 0 fail — up from pilot-112 11 (new tool selftests) |
| 10 | `python tools/fleet_failures.py scan` | exit 0; classes with counts in plain-reader text (`108 edit: Could not find oldString ...`, `85 task: Task cancelled`, `82 websearch: StatusCode ...`, `72 bash: Tool execution aborted`, `66 websearch: Missing key at [Q]`) — OK, no packet |
| 11 | `python tools/pack_check.py packs/fleet-vol-1` | RESULT PASS 13/0/0, exit 0 — pilot-112 stale-zip FAIL FIXED (zip resealed), no packet |
| 12 | `python tools/pack_check.py <scratch>/badpack` (fail path) | RESULT FAIL `FAIL pack.json: cannot read (.../pack.json)` exit 1 — fail path names why, no packet |

## Filed

- None. Two pilot-112 findings verified fixed (qa-shape message, stale zip); scaffold no-target make exit 0 stays K-54 OWNER (verdict pending); 336-byte scaffold ships nowhere (both export paths hold).

## Guards

- Scratch stayed under `$env:TEMP\opencode\` (pilot-113 only); one accidental default-path make (`skills/pilot-113-demo`, `work/pilot-113-demo`) removed immediately.
- No export with `--out` inside `skills/`.
- `Get-ChildItem skills -Recurse -Directory -Filter export` → nothing; no path over 240 chars under packs/.
- `git status --short -- book2skill mcp_server tools skills tests work` → empty, no pilot files.
