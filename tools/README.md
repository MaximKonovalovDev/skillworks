# tools

Helper scripts. Run them from the repo root.

- `b2s.py` - runs the book2skill command by file path (same as `python -m book2skill`).
- `new_skill.py` - stamps a new skill from `skills/_template`. `--check <name>` lists the slots still open.
- `pack_build.py` - builds the buyer files of a pack from its `pack.json`.
- `part_score.py` - prints one score line per team part.
- `gen_run_pairs.py` and `run_pairs.tmpl` - make the 4 `scripts/run_pairs.py` copies. Edit the template, never a copy.
- Other scripts (for example `skill_lint.py`, `skill_trial.py`, `eval_score.py`, `edit_guard.py`): read the first lines of each file.
- Open first: `b2s.py`, then `new_skill.py`.
