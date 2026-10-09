# evals

Test questions for the skills, and the results of test runs.

- `<skill>_qa.jsonl`: questions made from the source of one skill. The eval gate reads these.
- `<skill>_trials.jsonl`: trial runs of one skill.
- `sample_qa.jsonl`: a small sample to try the eval command.
- Some files are dated results, for example `edit-reread_reseal_2026-10-05.json`.
- Open first: `sample_qa.jsonl`, then the `<skill>_qa.jsonl` of the skill you work on.
- Run one: `python -m book2skill eval --work work/<name> --skill skills/<name> --qa evals/<name>_qa.jsonl`.
- Rate below 0.6 refuses export. Fix the skill, not the test.
