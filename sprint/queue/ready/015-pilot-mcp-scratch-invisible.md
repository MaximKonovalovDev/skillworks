---
role: builder
title: MCP skill_search serves only repo-root skills/; scratch-built skill invisible
---

Goal: A stranger who builds a skill to any `--skill` path (as the README shape allows) can query it via `python mcp_server/server.py`, or gets a clear "unknown skill / not served" message instead of silent `[]`.

Scope: `mcp_server/server.py` (skills-dir resolution + unknown-skill reply) + one test + one README line if a flag is added. No seed-skill changes.

Proof (pilot-view-r3, 2026-10-03, scratch dirs only in `%TEMP%\opencode\pilot-r3`, repo untouched):
- `python -m book2skill extract --in src\demo.md --out work` → exit 0 `extracted 9619 chars (text)`
- `python -m book2skill split --work work` → exit 0 `split into 2 chunks`
- `python -m book2skill index --work work` → exit 0 `indexed 2 records`
- `python -m book2skill build --work work --skill skill --name pilot-r3-demo --description "..."` → exit 0 `built ...\skill (1218 note chars)`
- `python -m book2skill audit --skill skill` → exit 0, 514 tokens over 6 sections
- `python -m book2skill eval --work work --skill skill --qa evals/sample_qa.jsonl` → exit 0 `total 3, passed 3, rate 1.0`
- `python -m book2skill export --skill skill --target claude --out dist` → exit 0 `dest ...\dist\claude\skill`
- MCP `initialize` → exit 0 handshake OK; `tools/list` → skill_search advertised.
- MCP `skill_search {"query":"gateway lanes chat vision lease"}` → exit 0, hits only from repo-root seeds (`flax-forge-ops`, `freud-dream-psychology`, `progit-branching`); scratch skill absent.
- MCP `skill_search {"query":"gateway","skill":"pilot-r3-demo"}` → exit 0 `[]` — no "unknown skill" hint, no hint which dir was searched.
- Root cause: `SKILLS = ROOT / "skills"` is hardcoded; there is no `--skills-dir` flag, env override, or per-call path. A skill built anywhere else (including the README's own `skills/mybook` example when the repo is installed elsewhere) is unqueryable by design, and a typo'd skill name is indistinguishable from "no matches".
- Note: tree's `server.py` is mid-flight K-29 work (159 lines vs committed 78: inputSchema + `is_error` envelope verified working — empty query returns `isError` envelope, exit 0). This packet targets only the hardcoded dir + silent-`[]` behavior, not the in-flight schema work.

User sees differently: after building, `skill_search` with their skill name returns hits from their skill (or the server says `unknown skill 'x'; serving N skills from <dir>`), instead of silent `[]`.

Stop: M 30 min for the packet; fix sized S/M. Proof for DONE: out-of-tree scratch skill returns hits via a documented override + unknown-skill query names the served dir + `python -m pytest tests/ -q` green with a new test.
