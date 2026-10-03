# pilot-view-r1 run log (2026-10-03T21:00Z)

Stranger-run against changes since r5 (2026-10-03T14:54Z): `make` one-command
(K-47/2c73e37), fleet skills pwsh-for-bash-writers/git-one-branch/
real-browser-automation/bevy-rust-ecs (b30ad39), arsenal tools (47b253d).
Scratch only (`%TEMP%\pilot-r1`), repo `work/ skills/ book2skill/ mcp_server/
tests/ README.md VISION.md sprint/board.md` untouched (`git status --short`
on those paths shows only pre-existing K-41 worktree edits to
`book2skill/export.py` + untracked `tests/test_export_zip.py`, both claimed
by builder-rows-r1 at 20:56Z). Own-words 760-char 2-doc harbor/beacon source.
No code, no commits.

Pipeline (`make` on docs folder, scratch work/skill):

| # | command | exit | one-line output |
|---|---|---|---|
| 1 | `make --in src --name pilot-r1-demo --description "Use when ..." --qa qa.jsonl` (question/answer/keywords shape) | 1 | raw traceback, `KeyError: 'q'` at `book2skill/eval.py:42` → packet 018 |
| 2 | same with `{"q","must"}` QA | 0 | `extract folder, 760 chars, 2 files / split 1 / index 1 / build ... / eval 3/3 = 1.000 (gate 0.6) / audit 6 files, 366 tokens / receipt make.json` |
| 3 | `export --skill <scratch> --target claude --out <scratch>/dist` | 0 | `dest .../dist/claude/pilot-r1-demo` + ZIP with 7 files (K-41 in-flight feature works on the stranger path) |
| 4 | `audit --skill <scratch>` | 0 | 366 tokens over 6 sections |
| 5 | `make --glob "*.md" ...` (double-quoted, pwsh) | 2 | `Got unexpected extra arguments (FINISH-LINE.md README.md ...)` — pwsh expanded `*.md` against repo CWD before python saw it; shell behavior, not filed (docs example `--glob "about_*.md"` never matches CWD so is safe) |
| 6 | `make --glob 'harbor*' ...` | 0 | `extract folder, 383 chars, 1 files / eval 2/3 = 0.667 (gate 0.6)` — glob itself works |
| 7 | `pytest tests/ -q` | 1 | 4 failed (all `tests/test_export_zip.py`, CRLF-vs-LF `assert body == ...` line-ending mismatch), 146 passed, 27 skipped in 61 s — failures sit in K-41's uncommitted in-flight work (worktree `export.py` + untracked test, claimed 20:56Z), NOT filed to avoid colliding with the owning run |
| 8 | MCP `--skills-dir <scratch>/skills`: initialize + tools/list | 0 | handshake OK, `[skill_search, skill_preview]` |
| 9 | `skill_search {"query":"harbor lantern"}` | 0 | scratch hit with rank/trust fields (`version/author/downloads/installs/stars/verified/eval_rate/above_gate`) |
| 10 | `skill_preview {"skill":"pilot-r1-demo"}` | 0 | SKILL.md head served |
| 11 | `skill_search {"query":"harbor","skill":"pilot-r1-demmo"}` | 0 | `unknown skill 'pilot-r1-demmo'; serving 1 skills from ...` envelope (`isError`+`is_error`) |
| 12 | `audit --skill skills/pwsh-for-bash-writers` | 0 | runs on committed fleet skill (SKILL.md: name matches dir, trigger description, licence line) |

Fixed behaviors confirmed (no packets): r5 items still hold (scratch-serving,
rank/trust + gate-first, preview, K-36 refusal, unknown-skill envelope);
`make` end-to-end on docs folder + `--glob` filtering + receipt `make.json`.

Filed: `sprint/queue/ready/018-pilot-make-qa-shape-crash.md`.
Not filed: zip-test line endings (K-41 in-flight, owned), pwsh `*.md` expansion (shell, docs safe).

Cleanup: scratch root `%TEMP%\pilot-r1` left for inspection (outside repo); repo tree unchanged, no commits.
