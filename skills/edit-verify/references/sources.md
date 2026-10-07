# Sources and licences (verified 2026-10-06)

The skill text and every pair are written fresh. The pages below were read to check each rule. No page text is copied.

- cline/cline (Apache-2.0, licence spdx read live 2026-10-06 via `gh api repos/cline/cline --jq .license.spdx_id`, pinned commit cd80a20 dated 2026-10-06, https://github.com/cline/cline): the checked source for the verify-edited-files idea (re-read the file after the edit and confirm the change is on disk before closing).
  - Sections used for the rules: re-read after every edit; quote the fresh lines before a follow-up edit; read the diff before closing.
- aider-ai/aider (Apache-2.0, licence spdx read live 2026-10-06 via `gh api repos/aider-ai/aider --jq .license.spdx_id`, pinned commit 5dc9490 dated 2026-05-22, https://github.com/aider-ai/aider): the checked source for the lint-after-edit idea (run the checks after the change and re-run until green).
  - Sections used for the rules: run the lint after every code edit; re-run after each fix; paste the real error line, never a paraphrase.
- sst/opencode packages/opencode/src/tool/edit.ts (MIT, licence spdx read live 2026-10-06 via `gh api repos/sst/opencode --jq .license.spdx_id`, file blob a92e4720, https://github.com/sst/opencode): the checked source for the exact-match edit shape (identical oldString is a no-op, short matches stay ambiguous until widened).
  - Sections used for the rules: refuse the no-op by verifying; count first and land a single change; close with paths plus results plus unverified gaps.
- Measured on this PC, not taken from a page: the red replay (109 Could-not-find oldString misses in 48 h per `python tools/fleet_failures.py scan` on 2026-10-07, plus 29 multiple-matches) and the pair results (`pairs.json`, pwsh 7), each bad side throwing the real line of `target-class.json`.
- This skill is original work under MIT. It is free to use and share.

Credit line for THIRD_PARTY_NOTICES.md: cline/cline (Apache-2.0, read live 2026-10-06, pinned cd80a20) plus aider-ai/aider (Apache-2.0, read live 2026-10-06, pinned 5dc9490) plus sst/opencode edit.ts (MIT, read live 2026-10-06) - verify-after-edit plus lint-after-edit plus exact-match ideas for skills/edit-verify; own words and own pairs, no text copied.
