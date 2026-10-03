---
role: builder
title: build accepts --name that breaks the name-matches-dir rule (silent invalid skill)
---

Goal: `build` refuses (or loudly warns) when `--name` does not match the skill dir basename or breaks the `a-z0-9-` rule, so a stranger never unknowingly produces a rule-violating skill.

Scope: `book2skill/build.py` (+ `book2skill/cli.py` wiring) + one test in `tests/test_pipeline.py`. No README change (rule already documented there).

Proof (pilot-view-r3, 2026-10-03, scratch dirs only in `%TEMP%\opencode\pilot-r3`, repo untouched):
- `python -m book2skill build --work work --skill ...\skill --name pilot-r3-demo --description "..."` → exit 0 `built ...\skill (1218 note chars)`.
- Resulting `SKILL.md` frontmatter: `name: pilot-r3-demo` while the directory is `skill/` — violates README rules "name matches dir, `a-z0-9-` only", with no warning.
- Downstream effect: `python -m book2skill export --skill skill --target claude --out dist` → exit 0 `dest ...\dist\claude\skill` — the shipped bundle is named after the dirname (`skill`), not the frontmatter name, so the stranger ships a misnamed artifact.
- Root cause: `_frontmatter()` sanitizes but `build()` never compares `name` against `skilldir.name` and never validates the charset; CLI takes any string.

User sees differently: a mismatched `--name`/`--skill` pair fails fast with `Error: --name 'x' must match skill dir 'y' (a-z0-9-)`, instead of an exit-0 build that quietly violates the layout spec and misnames the export.

Stop: M 30 min for the packet; fix sized S. Proof for DONE: mismatched pair refused (exit != 0) with the naming rule quoted + matching pair still builds + `python -m pytest tests/ -q` green with a new mismatch test.
