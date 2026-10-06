---
name: edit-abort-guard
description: Use when a file edit comes back Tool execution aborted after a long call: slice to one small hunk with a timeout, run that hunk alone, then report with PASS.
version: 0.1.0
author: skillworks
tags: [edits]
license: MIT
---

# Slice small, run once, report the abort

A file edit that lands a large change in one call comes back `Tool execution aborted`. Sessions rerun the same whole edit and each comes back aborted again. Never rerun the whole edit after an abort. Slice the change to one small hunk with a scope plus a timeout, run that one hunk alone, then report the diff or the receipt with PASS.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_edit.py`, and the failure class is `references/target-class.json`. Each good side lands its hunk and prints the diff or the receipt report it promises.

## Slice every edit

- Slice every edit to one small hunk with `$l = Get-Content -LiteralPath big.txt` then `$l[2] = 'line 03 edit hunk fixed'` and report `slice hunk PASS small window` [src: references/pairs.md#ea-slice]
- Edit one small section with `$l = Get-Content -LiteralPath notes.md` then `$l[1] = 'slice small hunks only.'` and report `small check PASS sliced hunk` [src: references/pairs.md#ea-check]

## Halve after an abort

- Halve a failing edit to one hunk with `$l = Get-Content -LiteralPath big.txt` then `$l[10] = 'line 11 edit hunk fixed'` and run that hunk alone with `halve slice PASS one hunk alone` [src: references/pairs.md#ea-halve]
- Halve the retry with `$l = Get-Content -LiteralPath big.txt` then `$l[4] = 'line 05 edit hunk fixed'` and run that hunk alone with `halved hunk PASS run alone` [src: references/pairs.md#ea-half]

## One hunk, then stop

- Run one single hunk edit with `$l = Get-Content -LiteralPath big.txt` then `$l[0] = 'line 01 edit hunk fixed'` and stop after one abort with `single hunk PASS stopped once` [src: references/pairs.md#ea-single]
- Try one small hunk only with `$l = Get-Content -LiteralPath notes.md` then `$l[1] = 'one hunk only.'` then stop after the abort with `once hunk PASS stopped abort` [src: references/pairs.md#ea-once]

## Check size, background long edits

- Check the size first with `Measure-Object -Line` then slice with `$l = Get-Content -LiteralPath big.txt` and report `size check PASS sliced small` [src: references/pairs.md#ea-size]
- Check the size with `Measure-Object -Line` before any unbounded section edit and report `size first PASS sliced hunk` [src: references/pairs.md#ea-first]
- Move a long edit to the background with `Set-Content -LiteralPath receipt.txt` plus a timeout, poll the receipt with `Test-Path -LiteralPath receipt.txt`, report `background receipt PASS polled` [src: references/pairs.md#ea-back]
- Poll the receipt with `Get-Content -LiteralPath receipt.txt -Raw` under a timeout and report `receipt poll PASS background edit` [src: references/pairs.md#ea-poll]

## Stop after the abort and report

- Close an abort with `RESULT report PASS hunk` naming the hunk used [src: references/pairs.md#ea-report]
- Record the run with `RESULT record PASS reported` listing the hunk used and the edit result [src: references/pairs.md#ea-record]

## When an edit aborts

Fix the cause once. Do not send the same whole edit again. The error text names the cause: look it up in `references/errors.md`.
