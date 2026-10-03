# pilot-view-r4 run log (2026-10-03T14:10Z)

Stranger-run of the README Use block after K-28 (Gutenberg strip) + K-29/015
(--skills-dir + unknown-skill envelope + inputSchema validation) landed.
Scratch dirs only (`%TEMP%\pilot-r4`), repo `skills/` and `work/` untouched
(`git status --short -- work skills book2skill mcp_server tests README.md`
empty). Own-words 2605 B harbor demo source. No code fixes, no commits.

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `python -m book2skill --help` | 0 | 8 commands listed (extract/split/index/build/audit/eval/refresh/export) |
| 2 | `extract --in src\demo.md --out work` | 0 | `extracted 2605 chars (text)` |
| 3 | `split --work work` | 0 | `split into 1 chunks` |
| 4 | `index --work work` | 0 | `indexed 1 records` |
| 5 | `build --work work --skill skill --name pilot-r4-demo --description "..."` | 0 | `built ...\skill (608 note chars)` — frontmatter `name: pilot-r4-demo` vs dir `skill/`, no warning → 016 STILL REPRODUCES (verbatim: exit 0, mismatch silent) |
| 6 | `audit --skill skill` | 0 | 354 tokens over 6 sections |
| 7 | `eval --work work --skill skill --qa evals/sample_qa.jsonl` | 0 | `total 3, passed 1, rate 0.3333` (sample QA is unrelated content — diagnostic, expected) |
| 8 | `export --skill skill --target claude --out dist` | 1 | `eval gate refused export: rate 0.333 below 0.6; fix the skill first` — gate correct, not a defect |
| 9 | MCP `initialize` + `tools/list` with `--skills-dir %TEMP%\pilot-r4` | 0 | handshake OK; skill_search advertised with inputSchema (query required; skill string; limit int 1-20 default 5) + CacheHint ttlMs 3600000 |
| 10 | MCP `skill_search {"query":"gateway lantern ferry ledger"}` via `--skills-dir` | 0 | 2 hits from scratch skill (`skill\chapters\notes.md` score 6, `skill\SKILL.md` score 1) → 015 FIX CONFIRMED |
| 11 | MCP `skill_search {"query":"gateway","skill":"pilot-r4-demmo"}` (typo) | 0 | `{"error": "unknown skill 'pilot-r4-demmo'; serving 1 skills from ...\pilot-r4"}` with `isError`+`is_error` → unknown-skill envelope CONFIRMED |
| 12 | MCP `skill_search {"query":"gateway","skill":"pilot-r4-demo"}` (frontmatter name, dir is `skill/`) | 0 | same unknown-skill envelope — server keys on DIR name, not frontmatter; downstream effect of 016's mismatch, not a new defect (fix 016 and the names agree) |
| 13 | MCP empty-query call | 0 | `{"error": "query is required (non-empty string)"}` envelope → K-29 validation intact |
| 14 | MCP `skill_search {"query":"beacon causeway","skill":"skill"}` via `$SKILLWORKS_SKILLS_DIR` env (no flag) | 0 | 1 hit from scratch notes.md score 3 → env override CONFIRMED |
| 15 | `extract` on 7-line fake-Gutenberg file (markers present) | 0 | `extracted 121 chars`, header gone but `*** END ... ***` + footer KEPT, `stripped:true` — `_END_MIN_LINE=100` guard skips footers in files under 100 lines. Documented tradeoff (comment in extract.py), real PG books are thousands of lines; noted as observation only, no packet |

Filed: none (015/016 already in ready/ — 015 fix confirmed verbatim above,
016 defect reproduced verbatim above; no other stranger-visible defects found).
Cleanup: scratch root `%TEMP%\pilot-r4` removed after run.
