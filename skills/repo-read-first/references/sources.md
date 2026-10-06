# Sources and licences (verified 2026-10-04)

The skill text and every pair are written fresh. The pages below were read to check each rule. No page text is copied.

- cli/cli (MIT, licence spdx read live 2026-10-04 via `gh api repos/cli/cli --jq .license.spdx_id`, pinned tag v2.88.1, https://github.com/cli/cli, licence text https://api.github.com/licenses/mit): the checked source for the check-first sequence.
  - README.md: `gh api` as the scriptable REST entry point and the repos record shape.
  - docs/source.md: read the repo record first for the default branch and licence before file reads.
  - docs/api-and-hosts.md: list the directory before reading, search then confirm the exact path, fall back to the git host when a service is unindexed.
  - Sections used for the rules: repos record first (default branch plus licence); directory listing before contents reads; contents call pinned to a resolved ref; never guess raw URLs.
- Measured on this PC, not taken from a page: the red replay (`gh api repos/owner/name` fails `gh: Not Found (HTTP 404)` on 2026-10-04) and the pair results (`pairs.json`, pwsh 7), each bad side throwing the real guessed-read line of `target-class.json`.
- v1.1.0 (2026-10-06): 5 new pairs (rr-b07 timeout retry, rr-b08 assumed branch, rr-b09 nested path, rr-b10 third repo, rr-b11 main raw) from the newest 48 h failures in failures.json (github_get_file_contents timeout 11, bad branch refs 2+2, path misses 24, wiki unindexed 3, raw 404s 39); own words and own pairs, no text copied.
- This skill is original work under MIT. It is free to use and share.

Credit line for THIRD_PARTY_NOTICES.md: cli/cli (MIT, licence spdx read live 2026-10-04 via gh api repos/cli/cli, pinned tag v2.88.1) - repos-record-first plus list-before-read plus pinned-ref ideas for skills/repo-read-first; own words and own pairs, no text copied.
