---
name: bash-abort-guard
description: Use when a bash shell call comes back Tool execution aborted after a long run
version: 1.1.0
author: skillworks
tags: [shell]
license: MIT (skill text and scripts, original work)
---

# Bound every shell call

A long foreground shell call comes back `Tool execution aborted`. Bound every call with a timeout, slice work into one small chunk, write inline code to a temp file and run the file, limit output to a few lines, and move heavy builds to background with a receipt poll.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_abort.py`, and the failure class is `references/target-class.json`.

## Bound with a timeout

- Bound every call with `timeout 60` so the run ends before the tool aborts it [src: references/pairs.md#bb-timeout]
- Wait in background with `Start-Job` and a timeout instead of a foreground wait [src: references/pairs.md#bb-background]
- Poll a receipt with `Get-Content receipt.txt` on a short loop with a bound [src: references/pairs.md#bb-receipt]
- Move a heavy build to background with `Start-Process` and read its receipt file [src: references/pairs.md#bb-build]

## Slice into one chunk

- Slice the suite with `Select-Object -First 1` and run one chunk alone [src: references/pairs.md#bb-slice]
- Cut a chained check with `Select-Object -First 40` running one check at a time [src: references/pairs.md#bb-chain]
- Run one chunk with `--filter one` and report the diff plus check results [src: references/pairs.md#bb-chunk]
- Sequence single calls with `Get-Content queue.txt` instead of chaining two checks [src: references/pairs.md#bb-single]

## File plus limit plus report

- Write inline code with `Set-Content script.ps1` to a temp file and run the file [src: references/pairs.md#bb-file]
- Limit output with `Select-Object -First 5` so a scan never floods the call [src: references/pairs.md#bb-limit]
- Cap tool output with `Out-String` piped to a small slice before quoting it [src: references/pairs.md#bb-output]
- Report the run with `Set-Content report.txt` listing timeout, slice, file, limit, and RESULT [src: references/pairs.md#bb-report]

## Heavy runners plus reruns

- Move a heavy test runner through a `wrapper background timeout receipt` to background and poll its receipt [src: references/pairs.md#bb-wrapper]
- After an abort never `rerun heavy command` halve to one `single slice timeout` filter alone [src: references/pairs.md#bb-halve]
- Never chain a heavy build plus verify run one `single timeout receipt` check alone [src: references/pairs.md#bb-unhook]
- Bound a long suite with `slice limit timeout` on one small chunk with a small limit [src: references/pairs.md#bb-bounded]
- Start a heavy job in `background receipt timeout` and poll its receipt on a short loop [src: references/pairs.md#bb-shortloop]
- Run checks across scopes as one `single limit timeout` call alone never chained [src: references/pairs.md#bb-scope]

## When a call aborts

Fix the shape once. Do not rerun the same long call. The error text names the cause: look it up in `references/errors.md`.
