---
name: read-abort-guard
description: Use when a file read comes back Tool execution aborted after a long call (large file in one read, rerun after the abort, chained reads, no offset and no limit, foreground wait, unclaimed queue packet read, whole brief after handoff): never rerun the whole read, slice to a small offset window with a limit and a timeout, run one slice alone, then report with PASS.
version: 0.3.0
author: skillworks
tags: [reads]
license: MIT
---

# Slice small, run once, report the abort

A file read that pulls the whole file in one call comes back `Tool execution aborted`. Sessions rerun the same whole read and each comes back aborted again. Never reread the whole file after an abort. Slice the read to a few lines with a small offset window and a limit plus a timeout, run that one slice alone, then report the lines or the receipt with PASS.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_read.py`, and the failure class is `references/target-class.json`. Each good side prints its lines or its receipt with the slice report it promises.

## Slice every read

- Slice every read to a few lines with `Get-Content -LiteralPath big.txt -TotalCount 5` and report `slice limit PASS small window` [src: references/pairs.md#ra-slice]
- Read one small section with `Get-Content -LiteralPath notes.md -TotalCount 2` and report `small check PASS sliced lines` [src: references/pairs.md#ra-check]

## Halve after an abort

- Halve a failing read to one window with `Select-Object -Skip 10 -First 3` and run that slice alone with `halve slice PASS one window alone` [src: references/pairs.md#ra-halve]
- Halve the retry with `Select-Object -Skip 4 -First 2` and run that slice alone with `halved window PASS run alone` [src: references/pairs.md#ra-half]

## One slice, then stop

- Run one single sliced read with `Get-Content -LiteralPath big.txt -TotalCount 2` and stop after one abort with `single slice PASS stopped once` [src: references/pairs.md#ra-single]
- Try one small slice only with `Get-Content -LiteralPath big.txt -TotalCount 1` then stop after the abort with `once slice PASS stopped abort` [src: references/pairs.md#ra-once]

## Check size, background long reads

- Check the size first with `Measure-Object -Line` then slice with `Get-Content -LiteralPath big.txt -TotalCount 2` and report `size check PASS sliced small` [src: references/pairs.md#ra-size]
- Check the size with `Measure-Object -Line` before any unbounded section read and report `size first PASS sliced window` [src: references/pairs.md#ra-first]
- Move a long read to the background with `Set-Content -LiteralPath receipt.txt` plus a timeout, poll the receipt with `Test-Path -LiteralPath receipt.txt`, report `background receipt PASS polled` [src: references/pairs.md#ra-back]
- Poll the receipt with `Get-Content -LiteralPath receipt.txt -Raw` under a timeout and report `receipt poll PASS background read` [src: references/pairs.md#ra-poll]

## Stop after the abort and report

- Close an abort with `RESULT report PASS slice` naming the slice used [src: references/pairs.md#ra-report]
- Record the run with `RESULT record PASS reported` listing the slice used and the read result [src: references/pairs.md#ra-record]

## When a read aborts

Fix the cause once. Never rerun the same whole read after an abort. The error text names the cause: look it up in `references/errors.md`.
