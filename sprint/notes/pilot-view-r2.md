# pilot-view-r2 notes (2026-10-03, run #2)

Clean-start pass as a stranger. Source: own scratch markdown in Temp (never committed).
Work/skill/dist scratch dirs removed after; `git status` shows only pre-existing loop state.

## Ran (all opened, all outputs read)
- `python -m pytest tests/ -q` → 7 passed (before, during, after).
- Full lane on scratch source: extract (320 chars, exit 0) → split (1 chunk) → index (1 record) → build → audit (JSON token report) → eval (`total 3, passed 1, rate 0.333`) → export (claude) → refresh (`changed, reindexed`, then `unchanged, no-op` on rerun).
- MCP stdio: initialize → protocolVersion 2024-11-05; tools/list → skill_search; tools/call skill_search "leases batch queues" → hit fresh pilot skill + flax-forge-ops. Handshake good.
- Read built `skills/pilot-view-demo/SKILL.md` (frontmatter name==dir, license MIT) and `dist/...` copy. Both opened, then deleted.

## Defects filed (sprint/queue/ready/)
- 002 README build line missing `--name`/`--description` → verbatim copy fails exit 2.
- 003 README eval line missing `--work` → verbatim copy fails exit 2.
- 004 export CLI never enforces the 0.6 eval gate (0.333 skill shipped, exit 0; gate dead code when report is None). Honesty gap vs AGENTS rule 2 / VISION R2.
- 005 unknown `--target` dumps a traceback instead of a usage error.

## Works today
pytest green, extract/split/index/audit/refresh-noop/export-copy/MCP handshake + search all good on first try.
