# skills

One folder per Agent Skill: 59 skill folders plus `_template`.

- Each skill folder has a `SKILL.md` with `name` and `description`. It may also have `references/`, `scripts/`, `tests/` and `evals/`.
- Open first: the `SKILL.md` of the skill you work on, for example `bash-abort-guard/SKILL.md`.
- New skill: do not hand-build one. Run `python tools/new_skill.py <name> "<description>"`. It copies `_template/`.
- The folder name must match the skill `name`: `a-z`, `0-9` and dashes only.
- Check one skill: `python -m book2skill audit --skill skills/<name>`.
- `skills/*/export/` is generated and git-ignored. Never commit it. Do not search or open it by a recursive walk; the long nested paths crash watchers.
