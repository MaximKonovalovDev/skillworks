# skillworks — book-to-skill ultra repo

One pipeline turns books and docs you own the rights to into Agent Skills
plus an MCP server. Seeds: your Forge/Flax docs (zero copyright risk) and
public-domain books (Project Gutenberg). No copyrighted books bundled.

## Setup

Requires Python 3.10+. Install dependencies first to avoid ModuleNotFoundError:

```powershell
pip install -r requirements.txt
python -m book2skill make --help   # then run the full pipeline from one command
```

## Pipeline (best parts combined, credited in THIRD_PARTY_NOTICES.md)

| Stage | Does | Stolen from |
|---|---|---|
| `extract` | PDF/EPUB/DOCX/MD/URL to text + metadata | book-to-skill, anything-to-skill |
| `split` | 5k-char Unicode chunks | BookToSkill |
| `index` | grounded JSONL knowledge index | BookToSkill |
| `build` | two-pass notes-then-skill: SKILL.md + chapters + glossary + patterns + cheatsheet | book-to-skill, anything-to-skill |
| `audit` | token-cost report per section | anything-to-skill |
| `eval` | source-derived Q&A, pass rate gate | anything-to-skill, spec eval guidance |
| `refresh` | fingerprint lock, rebuild only on change | anything-to-skill |
| `export` | claude, codex, opencode, gemini copy-layout exports | Skill_Seekers |

Delivery is triple like godot-agent: bundled skill + CLI + MCP server
(`mcp_server/` serves skill search over stdio).

## Export targets

`export --target <name>` writes an identical copy-layout export to
`dist/<target>/<name>/` with `SKILL.md` at the layout root; only the layout
root differs per target. Export is gated: eval rate >= 0.6, scaffold text
must be written first, same-version re-export is refused, and each export
writes `.lock.json` plus a sibling `<name>.zip`.

* `claude` — `dist/claude/<name>/` (`SKILL.md` at root)
* `codex` — `dist/codex/<name>/` (`SKILL.md` at root)
* `opencode` — `dist/opencode/<name>/` (`SKILL.md` at root)
* `gemini` — `dist/gemini/<name>/` (`SKILL.md` at root)

## Skill layout (agentskills.io spec)

```
skills/<name>/
  SKILL.md        # required frontmatter: name + description
  chapters/       # per-chapter notes
  glossary.md patterns.md cheatsheet.md
  references/     # one level deep, relative paths only
```

Rules: SKILL.md body under 500 lines, description states what + when in
third person with trigger keywords, name matches dir, `a-z0-9-` only.

## Use

```powershell
python -m book2skill extract --in <book.pdf> --out work/mybook
python -m book2skill split --work work/mybook
python -m book2skill index --work work/mybook
python -m book2skill build --work work/mybook --skill skills/mybook --name mybook --description "..."
python -m book2skill audit --skill skills/mybook
python -m book2skill eval --work work/mybook --skill skills/mybook --qa evals/sample_qa.jsonl
python -m book2skill export --skill skills/mybook --target claude --out dist
python mcp_server/server.py   # stdio MCP: skill_search
python mcp_server/server.py --skills-dir <dir>  # serve skills from elsewhere ($SKILLWORKS_SKILLS_DIR also works)
```

Proof: `python -m pytest tests/ -q`

## Seeds

* `skills/flax-forge-ops/` — hand-written from your own Forge docs,
  your own words, safe to publish.
* Public-domain: download from gutenberg.org yourself, never commit books
  you do not own.

## Honesty

No training, no fine-tuning, no vector DB here: retrieval is a JSONL index
with substring rank. Eval pass rate is a diagnostic, not a model metric.
