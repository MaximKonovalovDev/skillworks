# pilot-view-r3 run log (2026-10-03T13:53Z)

Stranger-run of the README Use block, scratch dirs only (`%TEMP%\opencode\pilot-r3`), repo `skills/` and `work/` untouched. Own-words 9622 B demo source.

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `python -m book2skill --help` | 0 | 8 commands listed (extract/split/index/build/audit/eval/refresh/export) |
| 2 | `extract --in src\demo.md --out work` | 0 | `extracted 9619 chars (text)` |
| 3 | `split --work work` | 0 | `split into 2 chunks` |
| 4 | `index --work work` | 0 | `indexed 2 records` |
| 5 | `build --work work --skill skill --name pilot-r3-demo --description "..."` | 0 | `built ...\skill (1218 note chars)` |
| 6 | `audit --skill skill` | 0 | 514 tokens, 6 sections |
| 7 | `eval --work work --skill skill --qa evals/sample_qa.jsonl` | 0 | `total 3, passed 3, rate 1.0` |
| 8 | `export --skill skill --target claude --out dist` | 0 | `dest ...\dist\claude\skill` |
| 9 | MCP `initialize` + `tools/list` | 0 | handshake OK, skill_search advertised (with inputSchema in current tree) |
| 10 | MCP `skill_search gateway lanes chat vision lease` | 0 | hits only from repo seeds; scratch skill absent |
| 11 | MCP `skill_search query=gateway skill=pilot-r3-demo` | 0 | `[]`, no unknown-skill hint → packet 015 |
| 12 | MCP empty-query call | 0 | `isError` envelope `query is required` (in-flight K-29 validation works) |
| 13 | `export --target bogus` | 2 | click Choice refusal (correct; an earlier `0` was a pipe artifact) |

Observations not filed as packets: `server.py` on disk is 159 lines vs committed 78 (K-29 editing live during this run — first read showed 78, execution used 159); export copies `eval_report.json` into the shipped bundle; bare `python mcp_server/server.py` hangs silently on stdin with no usage hint (stdio by design, noting only).

Filed: `sprint/queue/ready/015-pilot-mcp-scratch-invisible.md`, `016-pilot-build-name-dir-mismatch.md`.
Cleanup: scratch root removed after run.
