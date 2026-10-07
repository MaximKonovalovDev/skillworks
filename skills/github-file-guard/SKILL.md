---
name: github-file-guard
description: Use when a github_get_file_contents call comes back Failed to get file contents on a guessed path (nested path guess, repo record never read, directory passed as a file, rerun after the miss, branch-qualified guess, silent miss with no report): list the parent directory first, verify the path names a file, fetch only the verified path, then report with PASS.
version: 0.1.0
author: skillworks
tags: [github]
license: MIT (skill text and scripts, original work)
---

# List first, fetch only the verified file

A `github_get_file_contents` call on a guessed path in owner/name comes back `Failed to get file contents` with nothing fetched. Researcher runs guess nested paths, pass a directory where a file belongs, rerun the same guess after the miss, and file no report. Never fetch a guessed path and never rerun the same guess after a miss. List the parent directory first, verify the path names a file in the listing, fetch only the verified path, then report the run with PASS.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_github_file.py`, and the failure class is `references/target-class.json`. Each good side lists first and prints the verified report it promises.

## List the directory first

- List the parent directory with `Get-Content -LiteralPath listing.txt` before any content fetch and report `list verify PASS directory file` [src: references/pairs.md#gf-b01]
- Fetch one file with `Get-Content -LiteralPath listing.txt` listed first, the file verified in the list, and report `list verify PASS fetch file` [src: references/pairs.md#gf-g01]
- Stop after one miss with `Get-Content -LiteralPath listing.txt` as the single verify list and report `single stop PASS verify list` [src: references/pairs.md#gf-b04]

## Verify the path before the fetch

- Read the repo record with `Get-Content -LiteralPath record.txt` and fetch one single verified path, reporting `record verify PASS single fetch` [src: references/pairs.md#gf-b02]
- Read the record once with `Get-Content -LiteralPath record.txt` and take a single path, reporting `record single PASS fetch path` [src: references/pairs.md#gf-g02]
- Treat an uncertain path as a directory with `Get-Content -LiteralPath listing.txt` and verify file or not, reporting `directory verify PASS file verdict` [src: references/pairs.md#gf-g04]

## Fall back after a miss

- Fall back to a directory listing with `Get-Content -LiteralPath listing.txt` when a directory path misses and report `directory listing PASS fallback file` [src: references/pairs.md#gf-b03]
- Cover a miss with `Get-Content -LiteralPath listing.txt` as the fallback listing and report `stop listing PASS report miss` [src: references/pairs.md#gf-g03]
- Verify the branch with `Get-Content -LiteralPath record.txt` plus the path on that branch and report `branch verify PASS fetch pair` [src: references/pairs.md#gf-b05]

## Report the run

- Stop a silent miss with `Get-Content -LiteralPath listing.txt` and name the verified path, reporting `report RESULT PASS verified path` [src: references/pairs.md#gf-b06]
- Record the run with `Get-Content -LiteralPath listing.txt` plus the fetch result and close `record RESULT PASS listing fetch` [src: references/pairs.md#gf-g06]
- Confirm the branch in `Get-Content -LiteralPath record.txt` and verify the path on it, reporting `branch record PASS verify path` [src: references/pairs.md#gf-g05]

## When a file fetch misses

List once and verify before the fetch. Do not guess the path again. The error text names the cause: look it up in `references/errors.md`.
