---
name: staff-plus-operating
description: Operate as a staff-plus engineer with four archetypes plus a weekly checklist plus a decision record. Use when leading technical direction, staffing a hard problem, or writing a reviewable decision without a manager title.
version: 0.1.0
license: MIT (skill text and scripts, original work)
---

# staff-plus-operating

Turn a fuzzy senior task into a named archetype plus a checked list plus a filed decision. Headless: no network, no prompts. It reads one JSON brief and writes one markdown operating report.

## Use it

Run `scripts/staff_plus_operating.py` from this skill folder, or give its full path:

```powershell
python scripts/staff_plus_operating.py --input <brief.json> --out <report.md>
```

The first word of stdout is the answer:

- `OPERATE <archetype> checklist <p>/6 decision <title>`: exit 0. Wrote the report to the `--out` file. The archetype is one of `tech-lead`, `architect`, `solver`, `right-hand`. The report holds the archetype, the 6-line checklist, the options, the risks, and the choice block.
- `ERROR ...`: exit 2, nothing written. Causes, one clause each: input file missing, input is not JSON, a required field missing or bad, a bad scope value, fewer than 2 options, a bad review date, `--out` is the input file.

## Rules

- The scope must be one of the four exact lowercase values `team`, `multi-team`, `single-hard-problem`, `leader-support`. Any other word or letter case is refused with exit 2. The map is fixed: `team` gives `tech-lead`, `multi-team` gives `architect`, `single-hard-problem` gives `solver`, `leader-support` gives `right-hand`.
- The brief needs at least 2 non-empty options and a review date shaped `YYYY-MM-DD`. The checklist needs at least 1 risk or that line reads `FAIL`. A title over 120 characters is refused.
- It does not manage people, pick the choice for you, or call a model. It files the record you wrote so a reviewer can check it.

Archetypes, checklist, and decision shape: `references/archetypes.md`, `references/operating-checklist.md`, `references/decision-template.md`.
