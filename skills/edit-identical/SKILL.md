---
name: edit-identical
description: Use when an edit call comes back No changes to apply oldString and newString are identical: refuse the no-op, verify the file already holds the wanted text, and report the diff plus checks.
version: 0.1.0
author: skillworks
tags: [editor]
license: MIT
---

# Refuse the identical no-op, then verify, then report

An edit that sends identical oldString and newString comes back `No changes to apply: oldString and newString are identical.` The shape is a whole block copied as both sides after a prior edit already landed or from stale memory, never diffed before sending. Refuse the no-op before sending, verify the file already holds the wanted text, land one single hunk only when a change remains, then report.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_identical.py`, and the failure class is `references/target-class.json`. Each good side prints its report with the verify plus check results.

## Refuse the no-op before sending

- Refuse the no-op with `Get-Content -LiteralPath <file> -Raw` when oldString equals newString, verify the file already holds the wanted text and report verified PASS [src: references/pairs.md#ei-refuse]
- Diff the wanted text against the fresh file with `Compare-Object (Get-Content <file>)` before sending, if identical report verified lines and stop [src: references/pairs.md#ei-diff]
- Verify the already-satisfied request with `Select-String -Pattern <wanted> <file>` and refuse the no-op edit with PASS [src: references/pairs.md#ei-already]

## Read fresh and quote, never memory

- Quote six lines from the fresh `Read <file>` output with `Get-Content -LiteralPath <file>` before any follow-up edit on the same file [src: references/pairs.md#ei-quote]
- Read the fresh file with `Get-Content -LiteralPath <file> -Raw` after one identical miss, never retype oldString from memory [src: references/pairs.md#ei-fresh]
- Read the diff hunks with `git diff <file>` plus `git diff --stat` before closing and confirm the single intended change [src: references/pairs.md#ei-verify]

## Narrow to one unique hunk

- Narrow the old text to the one changed line with `Select-String -Pattern <old> <file>` and unique context, never copy a whole block as both sides [src: references/pairs.md#ei-narrow]
- Count first with `(Select-String -Pattern <old> <file>).Count` and land a single hunk only, never force a broad match [src: references/pairs.md#ei-single]
- Land one single hunk with `Edit <file>` using the quoted oldString, then stop after the single change [src: references/pairs.md#ei-hunk]

## Check once and report

- Run one single check with `python -m pytest tests/test_edit_identical.py -q` after the edit and never close while the check is red [src: references/pairs.md#ei-check]
- Keep the small hunk narrow with `Get-Content <file> | Select-Object -Skip 1 -First 3` and report the diff with PASS [src: references/pairs.md#ei-small]
- Close with the changed paths from `git diff --stat`, the check commands with their results, and a RESULT line plus PASS [src: references/pairs.md#ei-result]

## When an edit misses

Fix the cause once. Do not send the same text again. The error text names the cause: look it up in `references/errors.md`.
