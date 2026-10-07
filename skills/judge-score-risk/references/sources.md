# Sources and licences (verified 2026-10-07)

The skill text and every pair are written fresh. Nothing is copied from another repository.

- Origin: https://github.com/MaximKonovalovDev/skillworks (this repository, `skills/judge-score-risk/`).
- Licence: MIT. Verified 2026-10-07: the repository `LICENSE` file is the MIT licence, copyright Maxim Konovalov.
- Failure class: the doctor lane's 48 h failure scan, class `judge-score-risk` in `skills/judge-score-risk/references/target-class.json` (59 judge-agent read-missing guesses in 48 h, row DR-1007-4, scanned 2026-10-07; replayed live 2026-10-07: `Cannot find path 'packet/review-*.md' because it does not exist` in scratch under TEMP). Own MIT corpus, read live 2026-10-07.
- Donor ideas only, never vendored: qodo-ai pr-agent at 06a2991 (MIT, read live 2026-10-06 per research INDEX S49-02): added-lines-only scope plus untrusted-input guard plus YAML verdict with score plus effort plus risk plus merge enum plus fingerprint dedupe plus capped repo context. No donor text or code is copied.
- Distinct from DR-1007-1 DONE (skill `ready-file-check`, queue claim lead lock review inbox plus packet path misses for the trigger wording) and DR-1006-4 READY (skill `edit-verify`, lint-after-edit): this skill owns the judge scored-verdict shape only.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side reading a guessed packet path that was never committed.
- Every statement in `SKILL.md` is run against the real pairs by `tests/test_judge_score_risk.py`.

Credit line for THIRD_PARTY_NOTICES.md: judge-score-risk (MIT skill text and scripts, original work, failure class from own MIT corpus read live 2026-10-07; donor pr-agent MIT ideas only, no outside text copied).
