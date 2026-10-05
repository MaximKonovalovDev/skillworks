---
name: book-to-skill
description: Turn a manual, book or docs folder you may use into a tested Agent Skill with the skillworks book2skill pipeline. One command (make) extracts, splits, indexes, builds, evals and audits it, and exports only after the skill text is really written. Use when asked to build, refresh or export an Agent Skill from a PDF, EPUB, DOCX, markdown or text source, or to check a skill against the eval gate before it ships.
version: 0.1.0
license: MIT
---

# book-to-skill

book2skill makes the SCAFFOLD of a skill from a source and measures it. The scaffold is not a skill: you write the
skill from it. Nothing in the pipeline calls a model.

## Before you start

- Owned, licensed or public-domain sources only. The source text stays in `work/` (git-ignored), never in a commit. A
  NonCommercial source (for example Pro Git) is shared free and never sold. Credit every source with its licence in
  `references/sources.md` of the skill.
- Run from the root of the skillworks repo (`<skillworks>` below), or from any folder with
  `python <skillworks>/tools/b2s.py ...`. The defaults `work/<name>`, `skills/<name>` and `dist` are relative to the
  folder you stand in, so elsewhere pass `--work`, `--skill` and `--out` yourself or you create folders in that repo.

## The one command

```powershell
python tools/b2s.py make --in <file|folder> --name <kebab-name> --description "Use when ..." --qa evals/<name>_qa.jsonl
```

Add `--glob "about_*.md"` to take only some files of a folder, `--target claude` (repeat for codex, opencode, gemini)
to export, `--rebuild` to overwrite a SKILL.md an author wrote. Sources: `.pdf`, `.epub`, `.docx`, a text file, or a
folder of `.md`, `.mdx`, `.markdown`, `.rst` and `.txt` files (front matter dropped; hidden folders, `node_modules`,
`export` folders and links skipped). Use local files: a URL is not covered here.

It prints one line per stage: `extract`, `split`, `index`, `build`, `eval n/m = rate (gate 0.6)`, `audit`, `fill`,
`receipt`. The `fill` line names the files that still hold the scaffold text. Everything is in `work/<name>/make.json`.

## You write the skill

After `make`, SKILL.md, `glossary.md`, `patterns.md` and `cheatsheet.md` are placeholders and `chapters/notes.md` is raw
chunk heads. Read the chunks in `work/<name>/chunks/`, then write rules in your own words, each saying where in the
source it comes from, and replace the four files. Running `make` again keeps your SKILL.md (`build skipped`).
`export held` (exit 1) while any placeholder remains: a pack with placeholder text is not shipped.

## The QA file

One JSON object per line: `{"q": "a question an agent really asks", "must": ["words quoted from the source"]}`. Draw
8 or more questions from the failure the skill must fix. A question passes when every `must` string (any letter
case) appears in the top 5 chunks the search returns. A rate under 0.6 refuses everything after it
(`eval gate refused ... fix the skill, not the test`): fix the skill, never edit the QA to pass. Fleet skills
hold 0.9. The search splits the question on spaces and keeps punctuation, so `objects?` never matches `objects`: leave
the question mark off. A wrong shape is refused first: exit 2, `must be {"q", "must"}`.

## Export and the nesting guard

`--target` writes `<out>/<target>/<name>/` and `<out>/<target>/<name>.zip` with SKILL.md at the zip root. `--out` is
`dist`, never a folder inside `skills/` or inside the source. On 2026-10-03 an export nested in its own skill made paths
of thousands of characters and crashed the OpenCode server 9 times. The export refuses a path over 240 characters and
leaves `export` folders and links out of the copy. After any make or export, check
`Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing. `skills/*/export/` is git-ignored: regenerate,
never commit.

## When make refuses (exit 2, no skill built)

A name that is not kebab-case (a-z, 0-9, dashes) or differs from the skill folder; a missing QA file; a source that does
not exist; `--work` and `--skill` inside each other; either inside a source folder; no matching file in the folder. All
stages, one by one, and the budgets a shipped skill must meet (body 2000 tokens, description 40 to 1024 characters
with `Use when`): `references/stages.md`.
