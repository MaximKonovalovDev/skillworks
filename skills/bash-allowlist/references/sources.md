# Sources and licences (verified 2026-10-05)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/bash-allowlist/`).
- Licence: MIT. Verified 2026-10-05: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `bash-allowlist-denied` in `skills/bash-allowlist/references/target-class.json` (167 denied by policy calls in 48 h across 8 repos, row DR-1005-4, scanned 2026-10-05T09:43Z). Own MIT corpus, read live 2026-10-05.
- Licensed manual for the receipts: the two own MIT notes passed to `python -m book2skill make --in <folder> --name bash-allowlist` (single-call-no-pipe plus dedicated-tools, own words, read live 2026-10-05; receipt `work/bash-allowlist/make.json`).
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real prevents you from using this specific tool call line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_bash_allowlist.py`.

Credit line for THIRD_PARTY_NOTICES.md: bash-allowlist (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-05; no outside text copied).
