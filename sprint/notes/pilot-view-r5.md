# pilot-view-r5 run log (2026-10-03T14:54Z)

Stranger-run against MCP changes since r4: skill_search rank/trust fields +
gate-first sort (K-15/19), skill_preview (K-17), --skills-dir (015), build
name/dir refusal exit 2 (K-36). Scratch only (`%TEMP%\pilot-r5`), repo
`work/ skills/ book2skill/ mcp_server/ tests/ README.md VISION.md
sprint/board.md` untouched (`git status --short -- <those paths>` empty).
Own-words 9048 B 2-doc harbor/beacon source. No code, no commits.

Pipeline (2-doc scratch skill):

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `extract --in %TEMP%\pilot-r5\src\demo.md --out %TEMP%\pilot-r5\work` | 0 | `extracted 9047 chars (text)` |
| 2 | `split --work %TEMP%\pilot-r5\work` | 0 | `split into 2 chunks` |
| 3 | `index --work %TEMP%\pilot-r5\work` | 0 | `indexed 2 records` |
| 4 | `build --work work --skill skills\pilot-r5-demo --name pilot-r5-demo --description ...` | 0 | `built ...\pilot-r5-demo (1218 note chars)` |
| 5 | `audit --skill skills\pilot-r5-demo` | 0 | `514 tokens` over 6 sections (notes 1218 chars/314 tok, SKILL.md 335 chars/93 tok) |
| 6 | `eval --work work --skill skills\pilot-r5-demo --qa qa.jsonl` (2 source-derived Qs) | 0 | `total 2, passed 2, rate 1.0` |

MCP (`python mcp_server/server.py --skills-dir %TEMP%\pilot-r5\skills`):

| # | call | exit | verbatim result |
|---|---|---|---|
| 7 | `initialize` + `tools/list` | 0 | handshake OK; tools `[skill_search, skill_preview]`; skill_search inputSchema query required/skill string/limit int 1-20 default 5; both carry `_meta.cacheHint {"ttlMs":3600000,"scope":"public"}` |
| 8 | `skill_search {"query":"harbor lantern"}` (015 + K-15/19) | 0 | 2 hits, first: `{"skill":"pilot-r5-demo","file":"pilot-r5-demo\\chapters\\notes.md","score":33,...,"version":"0.1.0","author":"skillworks","downloads":2,"installs":1,"stars":5.0,"tags":[],"verified":true,"eval_rate":1.0,"above_gate":true,"installed":true}` — all 10 new fields present verbatim; second hit SKILL.md score 1 same meta |
| 9 | gate-first sort probe (second scratch skill `pilot-r5-low` with eval_report rate 0.0) `skill_search {"query":"harbor lantern","limit":5}` | 0 | order `pilot-r5-demo` (above_gate true, eval_rate 1.0, score 33) before `pilot-r5-low` (above_gate false, eval_rate 0.0, downloads 0, stars 0.0, verified false, score 33) at equal score — gate-first sort CONFIRMED |
| 10 | `skill_preview {"skill":"pilot-r5-demo"}` (K-17) | 0 | `{"skill":"pilot-r5-demo","file":"SKILL.md","head":"---\nname: pilot-r5-demo\n...","chars":335}` — README-then-SKILL.md fallback serves SKILL.md head |
| 11 | typo `skill_search {"query":"harbor","skill":"pilot-r5-demmo"}` | 0 | `{"error": "unknown skill 'pilot-r5-demmo'; serving 1 skills from C:\\Users\\me\\AppData\\Local\\Temp\\pilot-r5\\skills"}` with `isError:true` + `is_error:true` |
| 12 | typo `skill_preview {"skill":"pilot-r5-demmo"}` | 0 | same unknown-skill envelope shape as #11 (`isError`+`is_error`) |
| 13 | `build --name wrong-name` vs dir `pilot-r5-demo` (K-36) | 2 | `Error: --name 'wrong-name' must match skill dir 'pilot-r5-demo' (rule: name matches dir, a-z0-9- only)` — exit 2, rule quoted |

Fixed behaviors confirmed (no packets): 015 scratch-serving via --skills-dir;
K-15/19 rank/trust fields + gate-first sort; K-17 skill_preview; K-36 mismatch
refusal exit 2; unknown-skill envelope on both tools.

Filed: none. No NEW stranger-visible defects. K-09 freud rank is a known open
row (051-k09-rarity-rank.md) — not re-filed per instructions.

Cleanup: scratch root `%TEMP%\pilot-r5` left for inspection (outside repo, git-ignored by location); repo tree unchanged, no commits.
