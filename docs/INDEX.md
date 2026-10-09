# Index: skillworks

Start here. The rules for every agent are in `AGENTS.md`. The goal is `VISION.md`.

Proof (the test suite): `python -m pytest tests/ -q`

## Read first

1. `AGENTS.md` - the rules every agent reads first.
2. `VISION.md` - the goal and the finish bars.
3. `README.md` - what the repo is and the pipeline.
4. `book2skill/cli.py` - the command line (`python -m book2skill`).
5. `.opencode/repomap.md` - the file map of this repo.

## Folders

- `book2skill/` - the Python package. Turns a book or manual into a tested skill. Open `cli.py` first. See `book2skill/README.md`.
- `skills/` - 59 skill folders plus `_template`. Each has a `SKILL.md`. See `skills/README.md`.
- `evals/` - test questions per skill (`<skill>_qa.jsonl`) and trial logs. Open `sample_qa.jsonl` first. See `evals/README.md`.
- `tests/` - the pytest suite. Open `skill_stock.py` first. See `tests/README.md`.
- `tools/` - helper scripts. Open `b2s.py` or `new_skill.py` first. See `tools/README.md`.
- `packs/` - packs for sale (listing, free Vol 0 sample, price proof). Open `packs/catalog.md` first. See `packs/README.md`.
- `team/` - team notes for parts P1-P5, plus `compact-log.md`. Open `workspace.md` first. See `team/README.md`.
- `mcp_server/` - the stdio MCP server (`skill_search`, `skill_preview`). Open `server.py`.
- `prompts/` - versioned prompt text. Open `build-skill.md`.
- `docs/` - this index and `VIDEO-PACK.md`.
- `research/` - research notes. Open `research/INDEX.md` first.
- `findings/` - dated findings, for example `adopted-check-2026-10-06.md`.
- `from-design-studio/` - files sent from design-studio (one folder, `O-029`).
- `sprint/` - loop files (board, inbox, handoff, halt). Rules are in `AGENTS.md`.
- `.opencode/` - OpenCode loop config. Open `repomap.md` first.
- `.claude-plugin/` - plugin marketplace file (`marketplace.json`).
- `archive/` - old text. Searches skip it. Read it by path only.
- `work/` - books and build folders. Git-ignored. Never commit.
- `dist/` - built ZIPs (for example `fleet-vol-1.zip`). Git-ignored.
- `.tools/` - free tools installed in the repo. Git-ignored.

## Root files

- `README.md` - what the repo is, the pipeline and the export targets.
- `AGENTS.md` - the rules for every agent.
- `VISION.md` - the goal, the delivery bar and the intake list.
- `VISION-TABLES.md` - research tables.
- `FINISH-LINE.md` - what "done" means, as bars.
- `THIRD_PARTY_NOTICES.md` - credits for the parts we took from other projects.
- `LICENSE` - the licence.
- `steal-spec-mcp.md` - the spec for the MCP servers and the security gate.
- `requirements.txt` - Python packages.
- `arsenal.json` - this repo's tool list.
- `opencode.jsonc` - OpenCode settings.
- `orders.csv` - orders from other repos (one row per order).

## Rules to know

- `skills/*/export/` is generated and git-ignored. Never commit it. Do not search or open it by a recursive walk.
- Only owned or public-domain books. Never commit a copyrighted book.
- The eval gate: a rate below 0.6 refuses export. Fix the skill, not the test.
- `skills/freud-dream-psychology/chapters/notes.md` is huge: look up one id, never read it whole.
