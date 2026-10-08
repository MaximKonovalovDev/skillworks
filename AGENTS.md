# AGENTS: skillworks

Every agent reads this first. Loop `/sprint` (`.opencode/commands/sprint.md`); goal `VISION.md`.

1. Loop files: `sprint/board.md` (work), `sprint/handoff.md` (lead), `sprint/inbox.md` (asks), `VISION.md` (goal).
2. One branch `main`: pull first (`git pull --no-rebase --no-edit origin main`); own paths only, never `git add -A`, force-push, or history rewrite. Only the lead commits; helpers never commit or push.
3. A claim counts only with its proof command's one-line result in the commit body; a report alone proves nothing.
4. Files via Glob/Grep/Read/Edit/Write; shell per `## Shell and search`.
5. Never print/commit a secret, kill a process, or remove `sprint/halt`.
6. Never ask the owner mid-loop: his decision is an OWNER row on the board, loop goes on.

## Shell and search
- pwsh, not bash. UTC: `Get-Date -AsUTC -Format "yyyy-MM-ddTHH:mmZ"`. No grep/head/tail/wc/sed: Grep tool, `Select-Object -First/-Last N`, `(Get-Content f | Measure-Object -Line).Lines`.
- Code over one line goes to `$env:TEMP\opencode\<name>.mjs` (or `.py`) and runs there; never multi-line `node -e`/`python -c`.
- Glob skips dot folders from root: put `.opencode`/`.lanes` in `path`. Queue files (claims.txt, ready/, done/) by full path.

## Where things are (no src/ folder)

`book2skill/` package (extract, split, index, build, audit, eval, refresh, export, cli), `tests/`, `mcp_server/server.py`, `tools/part_score.py`, `prompts/`, `evals/<skill>_qa.jsonl`, `skills/<name>/`, `team/<part>.md`, `work/` (books, gitignored). `skills/*/export/` is ignored: regenerate, never commit. `sprint/lock.txt` lives only while a lead holds it; `sprint/queue/claims.txt` is created by the first claim. Kernel `tools/part-score.mjs` is `python tools/part_score.py` here; compactions logged in `team/compact-log.md`; `tools/b2s.py` runs the CLI by path. A new fleet skill is stamped, never hand-built: `python tools/new_skill.py <name> "<description>"` copies `skills/_template/` (its test file calls `tests/skill_stock.py`; `--check <name>` lists the `{{slot: ...}}` lines still open). The 4 `scripts/run_pairs.py` copies are made from `tools/run_pairs.tmpl` by `python tools/gen_run_pairs.py` (edit the template, never a copy; `--check` fails on drift). `python tools/pack_build.py packs/<slug> --starter` writes a pack's listing, buyer README, Vol 0 page and price file from `pack.json`. `packs/<slug>/` holds a pack for sale (listing, Vol 0, price evidence; its ZIP is made into git-ignored `dist/`), `.tools/` free tools installed inside the repo (git-ignored), and the doctor's private lane state lives in `C:/Users/me/.empire/state/skilldoctor/` (never committed). Other repos: `node C:/empire/center/arsenal.mjs --list` (own: `arsenal.json`). Old text: `archive/` (searches skip; Read by path).

## Pipeline (operator)

```powershell
# One command per manual (file, folder, URL): extract, split, index, build, eval, audit. --qa is yours (failure-drawn); --target also exports, held while scaffold text remains. An author's SKILL.md is never overwritten (--rebuild does). Receipt: work/<name>/make.json.
python -m book2skill make --in <file|folder|url> --name <name> --description "Use when ..." --qa evals/<name>_qa.jsonl [--glob "about_*.md"] [--target claude]
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

0. Only owned or public-domain sources; never commit copyrighted books; Gutenberg stays in `work/` (ignored).
1. SKILL.md frontmatter carries `name` + `description`; name matches dir.
2. Eval gate: rate below 0.6 refuses `export`. Fix the skill, not the test.
3. Refresh wins over rebuild: no-op when the fingerprint matches.
4. Every stage writes `work/<name>/receipt.json` with counts.
5. Export guard (2026-10-03 a nested export crashed the OpenCode server 9 times): `--out` only `dist`, never inside `skills/` or the source folder; after any make or export `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path passes 240 characters (`book2skill/export.py`, tests `test_export_guard.py` and `test_mcp_export_skip.py`).
6. This repo is public: no secret, and no other repo's text or numbers, in a committed file; those go to the private state folder above.

## Stage (Maxim 2026-10-08)

The empire is at its START. Never cite sales, revenue or "0 sales" as a finding, verdict, score or reason (audits, Lead 2, steals, reviews, inbox plans). Judge work by what it builds and whether it works.
