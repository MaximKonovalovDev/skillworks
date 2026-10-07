# Sources and licences (verified 2026-10-07)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/batch-first/`).
- Licence: MIT. Verified 2026-10-07: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan, class `batch-first` in `skills/batch-first/references/target-class.json` (16 GitHub MCP timeout misses in 48 h in 4 repos, row DR-1007-6, scanned 2026-10-07; replayed live 2026-10-07: `Request timed out` in scratch under TEMP). Own MIT corpus, read live 2026-10-07.
- Donors cline/cline (Apache-2.0) plus openai/swarm (MIT) per research INDEX S49-04 plus S49-05 read live 2026-10-06: batch-dispatch plus fan-out-collect ideas only, never vendored.
- Distinct from DR-1006-7 DONE (skill `websearch-retry`, websearch backend plus key plus timeout misses) plus BK-1007-3 DONE (skill `octokit-request`, octokit fetch-wrapper codes as book knowledge): this skill owns prompt-level batching of read-only calls only.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real timeout line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_batch_first.py`.

Credit line for THIRD_PARTY_NOTICES.md: batch-first (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-07; donor cline Apache-2.0 plus swarm MIT ideas only, no outside text copied).
