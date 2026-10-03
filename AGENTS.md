# AGENTS: skillworks

Every agent in this repo reads this first. The loop is `/sprint`
(`.opencode/commands/sprint.md`); the goal is `VISION.md`.

1. The files carry the loop: `sprint/board.md` (the work), `sprint/handoff.md`
   (where the lead is), `sprint/inbox.md` (asks from center and the owner),
   `VISION.md` (where we are going).
2. One branch, `main`. Pull before every push
   (`git pull --no-rebase --no-edit origin main`). Commit your own paths
   only (`git add <paths>`), never `git add -A`, never force-push, never rewrite
   history. Only the lead commits; helpers never commit or push.
3. A claim counts only with its proof command's one-line result in the commit
   body. An agent's report alone proves nothing.
4. Shell is pwsh. Use Glob, Grep, Read, Edit and Write for files.
5. Never print or commit a secret. Never kill a process, never remove
   `sprint/halt`.
6. The owner is never asked mid-loop: a decision only he can make is an OWNER
   row on the board, and the loop goes on.

## Where things are (look here first, no src/ folder exists)

`book2skill/` the package (extract, split, index, build, audit, eval, refresh,
export, cli), `tests/`, `mcp_server/server.py`, `tools/part_score.py`,
`prompts/`, `evals/<skill>_qa.jsonl`, `skills/<name>/`, `team/<part>.md`,
`work/` (books, gitignored). Export output `skills/*/export/` is ignored:
regenerate, never commit. `sprint/lock.txt` exists only while a lead holds it;
`sprint/queue/claims.txt` is created by the first claim (append, create if
missing). The kernel's `tools/part-score.mjs` is
`python tools/part_score.py` here; its `team/compact-log.md` does not exist yet
(create it on the first compaction).

## Pipeline lanes (operator)

```powershell
python -m book2skill extract --in <src> --out work/<name>
python -m book2skill split --work work/<name>
python -m book2skill index --work work/<name>
python -m book2skill build --work work/<name> --skill skills/<name>
python -m book2skill audit --skill skills/<name>
python -m book2skill eval --skill skills/<name> --qa evals/sample_qa.jsonl
python -m book2skill export --skill skills/<name> --target claude|codex|opencode|gemini
python -m pytest tests/ -q
python mcp_server/server.py
```

Rules:

0. Only feed sources you own or public-domain texts. Never commit
   copyrighted books. Gutenberg downloads stay in `work/`, ignored by git.
1. SKILL.md frontmatter must carry `name` + `description`; name matches dir.
2. Eval gate: pass rate below 0.6 refuses `export`. Fix the skill, not the test.
3. Refresh wins over rebuild: `refresh` no-ops when the fingerprint matches.
4. Receipts: every stage writes `work/<name>/receipt.json` with counts.
