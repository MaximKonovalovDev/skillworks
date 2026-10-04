---
name: _template
description: The template of a fleet skill. `python tools/new_skill.py <name> "<description>"` copies this folder into skills/<name>/, writes the name and description, and leaves slot lines to fill. Use when a new skill for the fleet is started, so its files and tests come from one shape.
license: MIT
---

# {{name}}

{{slot: one or two plain sentences: what the skill does, and that it is headless (no network, no prompts) when that is true.}}

## Use it

Run `scripts/{{script}}.py` from this skill's folder, or give its full path:

```powershell
python scripts/{{script}}.py --input <path> --out <path>
```

The first word of stdout is the answer:

- `{{slot: the success line the script prints, for example RUN <n> items ...}}`: exit 0. {{slot: what it wrote, and where.}}
- `ERROR ...`: exit 2, nothing written. {{slot: the causes, one clause each: missing input, bad value, refused path.}}

## Rules

- {{slot: the first rule a user could get wrong, with the exact value, case or limit.}}
- {{slot: the second rule.}}
- {{slot: what the tool does not do, so nobody expects it.}}

{{slot: one line that names the file in references/ holding the details, in backticks, or delete this line.}}
