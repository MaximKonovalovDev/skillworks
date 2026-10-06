---
name: fetch-github-first
description: Use when fetching a GitHub repo, file, or release with the web fetch tool and hitting 403 or 404: check the gh API record first, pin the ref, and fall back to the contents call.
version: 0.1.0
author: skillworks
tags: [github, fetch]
license: MIT
---

# Fetch the GitHub record first, never guess the URL

The web fetch tool guesses GitHub URLs and lands on 403 rate limit plus 404
misses on api.github.com, github.com, and raw.githubusercontent.com. Check the
gh API record first and every read lands. The full bad and good reports are
`references/pairs.md`, the machine list is `references/pairs.json`, the runner
is `scripts/run_fetch.py`, and the failure class is `references/target-class.json`.

## Record first (prove exists, pin ref, list path)

- Prove the repo exists with the repos call `gh api repos/OWNER/REPO` and note exists plus default branch plus licence before any file read with PASS [src: references/pairs.md#fg-b01]
- Verify the fetch target with the repos call `gh api repos/OWNER/REPO` then read the file with the contents call `gh api repos/OWNER/REPO/contents/FILE` and report PASS [src: references/pairs.md#fg-b02]
- Never fetch a guessed raw host URL with `webfetch`; read with the contents call `gh api repos/OWNER/REPO/contents/FILE?ref=REF` pinned to a ref with PASS [src: references/pairs.md#fg-b03]
- Ask the repos record for its default branch with `gh api repos/OWNER/REPO --jq .default_branch`, resolve the ref, then read with PASS [src: references/pairs.md#fg-b04]
- On a 403 rate limit call the repos call `gh api repos/OWNER/REPO` once, backoff and retry once, then read with the contents call with PASS [src: references/pairs.md#fg-b05]
- Read the directory listing `gh api repos/OWNER/REPO/contents/DIR` first, take the exact path from it, then read with the contents call with PASS [src: references/pairs.md#fg-b06]
- Run the full sequence with `gh api repos/OWNER/REPO` for the repos call plus default branch plus directory listing plus contents exact path with PASS [src: references/pairs.md#fg-g01]

## Fallback and report (licence, search, evidence)

- Prove exists with the repos call `gh api repos/OWNER/REPO` first, and when the web fetch misses use the fallback to the contents call with PASS [src: references/pairs.md#fg-g02]
- Resolve the pinned ref from the repos record with `gh api repos/OWNER/REPO --jq .default_branch` first, read with the contents call, and quote with PASS [src: references/pairs.md#fg-g03]
- Note the licence from the repos call `gh api repos/OWNER/REPO --jq .license` before reusing helper lines with PASS [src: references/pairs.md#fg-g04]
- Find helpers with search `gh search code --repo OWNER/REPO retry` first, confirm the exact path with the repos call and contents calls, then read with PASS [src: references/pairs.md#fg-g05]
- Report the record plus ref plus results plus unverified gaps with `gh api repos/OWNER/REPO` evidence in one closing block with PASS [src: references/pairs.md#fg-g06]
- Run the pair check with `python skills/fetch-github-first/scripts/run_fetch.py` before claiming the fetch is fixed [src: scripts/run_fetch.py#live-check]
