# Sources

Original work. No outside text, no outside code, nothing copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/inbox-file-reader/`).
- Licence: MIT. Verified 2026-10-04: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Idea: a least-privilege filing step, one input file, one output file and a suffix allowlist, so an autonomous triage
  agent cannot reach code. Written from scratch in `scripts/file_one_item.py`.
- Every statement in `SKILL.md` and `isolation.md` is run against the real script by `tests/test_inbox_file_reader.py`.
