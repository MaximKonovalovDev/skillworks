---
name: skill-eval-harness
description: Use when building or changing a book2skill skill and you must prove it triggers on the right prompts and answers from its own chunks before export.
---

# Skill Eval Harness

RED-GREEN for skills: run each QA prompt WITHOUT the skill (baseline),
then WITH it. If you never watched it fail without the skill, you do not
know the skill teaches anything. Fix the skill, never the test.

## 1. Baseline first (RED)

For every prompt in `evals/<name>_qa.jsonl`, record the unskilled answer:

```powershell
python -m book2skill eval --skill skills/<name> --qa evals/<name>_qa.jsonl
python -m pytest tests/ -q
```

Keep the failing outputs in `work/<name>/eval-baseline/` beside the receipt.

## 2. Triggering accuracy (SDO)

The frontmatter `description` is the trigger, not a summary. Rules:

- Start with "Use when ..." and list only symptoms, phrases, contexts.
- NEVER describe the skill's workflow in `description`; an agent will
  follow the description instead of reading the body.
- Add the words an agent would search for: error text, tool names,
  file types (`pwsh`, `book2skill`, `.pdf`, `SKILL.md`).
- Name with verb-first, hyphenated, matching the directory.

## 3. Evaluate (GREEN)

- Eval gate: pass rate below 0.6 refuses `export`. Widen the QA set
  (`grow_qa` from the failure the skill fixes), then re-run.
- Grade what the skill ANSWERS, not words in its own chunks.
- Save the report beside the skill; rerun `python -m pytest tests/ -q`.

## 4. Refactor

New rationalization found (agent dodges the skill)? Plug the loophole in
the body, keep the description trigger-only, re-verify baseline vs skill.

## Do not

- Skip the baseline run. Invent QA from the skill text instead of the
  failure it fixes. Weaken assertions to pass the 0.6 gate.
Source: https://github.com/obra/superpowers (MIT, fetched 2026-10-03)
