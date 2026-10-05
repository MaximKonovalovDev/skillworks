---
name: bash-spawn-guard
description: Use when a bash shell call comes back Unknown ChildProcess.kill after a long run
version: 1.0.0
author: skillworks
tags: [shell]
license: MIT (skill text and scripts, original work)
---

# One bounded call with a receipt

A long foreground shell call gets killed at the spawn layer and comes back `Unknown: ChildProcess.kill`. Never run long work bare in one foreground call. Slice to one small chunk with a timeout and a small output limit, write inline code to a temp file first, start detached work only with a receipt file, poll the receipt with a timeout, and report the diff and checks with a RESULT line and PASS.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_spawn.py`, and the failure class is `references/target-class.json`. Each good side prints its report with the diff plus check results.

## Start detached work only with a receipt

- Start a long check detached with `Start-Job receipt` writing to a receipt file to poll [src: references/pairs.md#bs-receipt]
- Move a verbose install to the `background receipt timeout` off the foreground call [src: references/pairs.md#bs-install]
- Wait in background with a `bounded wait timeout` instead of a sleep poll with no bound [src: references/pairs.md#bs-sleep]
- Poll a receipt with `Get-Content receipt.txt` on a short bounded loop with a timeout [src: references/pairs.md#bs-background]

## Slice to one small chunk

- Slice a suite with `slice one chunk timeout` running a single test file alone with a limit [src: references/pairs.md#bs-suite]
- Sequence chained checks with a `single check timeout` running one call alone with a limit [src: references/pairs.md#bs-chain]
- Run one small chunk with a `single chunk timeout slice` and report the lines [src: references/pairs.md#bs-chunk]
- Keep a listing to a `single listing limit timeout` with one command only [src: references/pairs.md#bs-list]

## File first, limit, report

- Write an inline probe with `Set-Content probe.txt` to a temp file before it runs [src: references/pairs.md#bs-inline]
- Run the file with a `run file timeout` and read its output with a small limit [src: references/pairs.md#bs-file]
- Bound a status check with a `short status timeout limit` of a few lines only [src: references/pairs.md#bs-short]
- Report the run with `Set-Content report.txt` listing command, receipt, RESULT, and PASS [src: references/pairs.md#bs-report]

## When a call is killed

Fix the shape once. Do not rerun the same long foreground call. The error text names the cause: look it up in `references/errors.md`.
