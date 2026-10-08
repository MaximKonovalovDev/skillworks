# book2skill

The Python package that turns a book, manual or doc into a tested Agent Skill.

- Command line: `python -m book2skill` (entry file `cli.py`).
- One command for the whole chain: `make` (extract, split, index, build, eval, audit, and export if asked).
- Stages: `extract.py`, `split.py` and `split_chapters.py`, `index.py`, `build.py`, `eval.py`, `audit.py`, `refresh.py`, `export.py`.
- Shared gates for the fleet skills: `gates.py`. Other module: `distill.py`.
- Every stage writes `work/<name>/receipt.json` with its counts.
- Open first: `cli.py`, then `make.py`.
- Tests for this package are in `tests/`.
