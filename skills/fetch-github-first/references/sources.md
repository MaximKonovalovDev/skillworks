# Sources and licences (verified 2026-10-06)

The skill text and every pair are written fresh. The pages below were read to check each rule. No page text is copied.

- cli/cli (MIT, licence spdx read live 2026-10-06 via `gh api repos/cli/cli --jq .license.spdx_id`, pinned tag v2.88.1, https://github.com/cli/cli, licence text https://api.github.com/licenses/mit): the checked source for the record-first sequence.
  - README.md: `gh api` as the scriptable REST entry point and the repos record shape.
  - Manual ("Fetch GitHub first", own MIT notes in the receipts): repos record first for the default branch and licence before file reads.
  - Sections used for the rules: repos record first (default branch plus licence); directory listing before contents reads; contents call pinned to a resolved ref; backoff on 403; never guess raw URLs.
- github/docs (CC-BY-4.0, licence read live 2026-10-06 via `gh api repos/github/docs --jq .license.spdx_id`, https://github.com/github/docs, licence text https://github.com/github/docs/blob/main/LICENSE): the checked source for REST repos plus contents plus search plus rate-limit rules.
  - REST repos record shape (default branch, licence); contents read pinned to a ref; code search then confirm; rate-limit backoff.
  - Sections used for the rules: repos record first; directory listing before contents reads; search then confirm the exact path; backoff on 403.
- Measured on this PC, not taken from a page: the red replay (`gh api repos/owner/name` fails `gh: Not Found (HTTP 404)` on 2026-10-06) and the pair results (`pairs.json`, pwsh 7), each bad side throwing the real 403/404 line of `target-class.json`.
- This skill is original work under MIT. It is free to use and share.

Credit line for THIRD_PARTY_NOTICES.md: cli/cli (MIT, licence spdx read live 2026-10-06 via gh api repos/cli/cli, pinned tag v2.88.1) plus github/docs (CC-BY-4.0, read live 2026-10-06) - repos-record-first plus list-before-read plus pinned-ref plus backoff ideas for skills/fetch-github-first; own words and own pairs, no text copied.
