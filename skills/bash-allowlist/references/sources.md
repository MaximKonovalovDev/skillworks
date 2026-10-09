# Sources and licences (verified 2026-10-09)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/bash-allowlist/`).
- Licence: MIT. Verified 2026-10-09: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan (`python tools/fleet_failures.py scan`), class `bash-allowlist-denied` in `skills/bash-allowlist/references/target-class.json` (260 denied by policy calls in 48 h across 12 repos, row DR-1006-6, scanned 2026-10-06T16:33Z; top fresh shapes node tools/lanes.mjs piped to Select-Object 14, gh repo piped to Select-Object 11, git stash piped to Select-Object 7, powershell -NoProfile, Start-Sleep plus Invoke-RestMethod plus ConvertTo-Json plus Select-Object). Own MIT corpus, read live 2026-10-06. Version bump 1.1.0 adds 5 pairs from the newest failures (ba-nested, ba-blocked, ba-sleep, ba-inline, ba-lanes); version bump 1.2.0 covers the 5 orphan pairs already in pairs.json plus trials (ba-stash, ba-diffpipe, ba-checkout, ba-lanes-echo, ba-getdate) with SKILL rules plus errors.md; no pair that passes was deleted.
- Licensed manual for the receipts: the two own MIT notes passed to `python -m book2skill make --in <folder> --name bash-allowlist` (single-call-no-pipe plus dedicated-tools, own words, read live 2026-10-06; receipt `work/bash-allowlist/make.json`).
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real prevents you from using this specific tool call line of `target-class.json`.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_bash_allowlist.py`.

Credit line for THIRD_PARTY_NOTICES.md: bash-allowlist (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-05; no outside text copied).
