---
name: repo-read-first
description: Use when reading a GitHub repo or asking a wiki service about one: check the repo record first, list before reading, and pin the ref instead of guessing the path, branch, or index state.
version: 1.0.0
author: skillworks
tags: [researcher, github]
license: MIT
---

# Read the repo record first, never guess

Researchers lose reads to three guessed things: the repo path, the file path, and the branch ref. Check the record first and every read lands. The full bad and good reports are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_pairs.py`, and the failure class is `references/target-class.json`.

## Check-first sequence (repo exists, path listed, ref pinned)

- Prove the repo exists with `gh api repos/OWNER/REPO` and note its default branch and licence before any file read [src: docs/source.md#repos-record-first]
- Verify the wiki is indexed before asking it, and fall back to the git host with `gh api` files when it reports unindexed [src: references/pairs.md#rr-b01]
- List the directory with `gh api repos/OWNER/REPO/contents/PATH` before reading any file path you did not list [src: docs/api-and-hosts.md#list-before-read]
- Take the exact path from that listing and read it with `gh api repos/OWNER/REPO/contents/EXACT --jq` instead of guessing [src: references/pairs.md#rr-b02]
- Never fetch a guessed raw host URL; read with the contents call pinned to a ref with `gh api repos/OWNER/REPO/contents/FILE?ref=REF` [src: references/pairs.md#rr-b03]
- Resolve the ref from the repo record first with `gh api repos/OWNER/REPO --jq .default_branch`, never assume trunk or main [src: references/pairs.md#rr-b04]

## Fallback and report (licence, search, evidence)

- Note the licence from the repos record with `gh api repos/OWNER/REPO --jq .license` before reusing any helper lines [src: docs/source.md#licence-from-record]
- Find helpers with search first, then confirm the exact path with `gh api repos/OWNER/REPO/contents/PATH` before quoting [src: docs/api-and-hosts.md#search-then-confirm]
- Treat a directory path as a listing, never as a file read: read `gh api repos/OWNER/REPO/contents/DIR` then the exact file [src: references/pairs.md#rr-b06]
- Report the repos record result, the resolved ref, and the contents lines with `gh api` evidence in one closing block [src: references/pairs.md#rr-g06]
- State what is still unverified with `unverified: <path or ref>` instead of filing a silent gap [src: references/pairs.md#rr-g06]
- Run the pair check with `python skills/repo-read-first/scripts/run_pairs.py` before claiming the read is fixed [src: scripts/run_pairs.py#live-check]
