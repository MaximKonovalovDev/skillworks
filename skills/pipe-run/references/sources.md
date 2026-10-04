# Sources

Original work. No outside text, no outside code, nothing copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/pipe-run/`).
- Licence: MIT. Verified 2026-10-04: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Idea: price a batch before it runs and refuse it over a ceiling, the general budget-guard pattern. The unit
  `chars // 4` is the token estimate `book2skill/audit.py` of this repository already uses. Written from scratch in
  `scripts/pipe_run.py`.
- Every statement in `SKILL.md` and `cost-model.md` is run against the real script by `tests/test_pipe_run.py`.
