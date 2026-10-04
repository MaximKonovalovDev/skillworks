---
role: builder
title: placeholder skill ships past make and direct export (only make --target holds it)
---

Goal: No command path hands a stranger a shippable bundle of placeholder text.
A fresh `make` on a small docs folder writes a pure-scaffold skill
(`SKILL.md` = "Built from owned sources", plus placeholder
`glossary.md`, `patterns.md`, `cheatsheet.md`) and passes; the direct
`export` CLI then zips it with exit 0. Only `make --target` refuses.
Close the bypass so every ship path holds placeholder text.

Scope: `book2skill/export.py` (refuse when `scaffold_leftovers(skill)`
is non-empty, with the same `export held: ... still hold the scaffold
text` message `make.py:96` already uses) + `book2skill/make.py`
(no-target run on a pure scaffold refuses instead of `gate pass`) +
one test with a scratch scaffold skill (direct export refused, message
names the files). No gate-arithmetic change; the `fill` line stays as
the authoring hint.

Proof (pilot-105, 2026-10-04T08:30-09:00Z, scratch only in
`$env:TEMP\opencode\pilot-105\`, repo product paths untouched):
- Scratch docs folder: 2 own-words files (harbor.md, beacon.md, 469 chars),
  QA in the `{"q","must"}` shape (3 questions).
- `python -m book2skill make --in <src> --name pilot-105-demo
  --description "Use when ..." --qa qa.jsonl --work <scratch> --skill <scratch>`
  → exit 0: `extract folder, 469 chars, 2 files / split 1 chunks /
  index 1 records / build ... / eval 3/3 = 1.000 (gate 0.6) / audit 6 files,
  330 tokens / fill SKILL.md, glossary.md, patterns.md, cheatsheet.md still
  hold the scaffold text / receipt make.json` with `"placeholders": [4 files],
  "gate": "pass"`.
- `SKILL.md` as written is 363 bytes: frontmatter + `# pilot-105-demo` +
  `Built from owned sources. Start with ...` (same scaffold shape as the
  card's 617-byte example; size differs only by name/description length).
- `python -m book2skill export --skill <scaffold> --target claude
  --out <scratch>/dist` → exit 0, `zip_files: 7`; the zip's `SKILL.md`
  is the same 363-byte placeholder (read back from the zip).
- Contrast: same `make` with `--target claude --out <scratch>/dist` → exit 1
  `export held: SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold
  the scaffold text; write them first (a pack with placeholder text is not
  shipped)`.
- Pinned today: `tests/test_book_to_skill.py:122` and
  `tests/test_make.py:98` pin the hold ONLY on the `make --target` path;
  no test covers direct `export` on a scaffold skill.
- Baselines this run: `python -m pytest tests/ -q` → 333 passed, 107 skipped;
  `node C:/Users/me/Desktop/center/arsenal.mjs --check skillworks` →
  RESULT PASS 11/0/0; `python tools/fleet_failures.py scan` prints classes
  with counts and human-readable error text (top: `173 task: Task cancelled`);
  `python tools/pack_check.py packs/fleet-vol-1` → RESULT PASS (10 checks,
  3 store-asset NEEDS); on an empty stub dir → `FAIL pack.json: cannot read
  ...` + `RESULT FAIL`, exit 1.

User sees differently: `export` (or `make`) on a skill whose placeholder
files nobody wrote over fails with `export held: <files> still hold the
scaffold text` naming what to write, instead of producing a `dist/` bundle
and ZIP that look shippable but contain "Built from owned sources".

Stop: M 30 min for the packet; fix sized S. Proof for DONE: scaffold skill
refused on the direct-export path with the files named + `make --target`
still held + a filled skill still ships + `python -m pytest tests/ -q`
green with the new refusal test.
