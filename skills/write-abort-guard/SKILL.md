---
name: write-abort-guard
description: Use when a file write comes back Tool execution aborted after a long call: slice to one small chunk with a timeout, write that chunk alone, then report with PASS.
version: 0.1.0
author: skillworks
tags: [writes]
license: MIT
---

# Slice small, write once, report the abort

A file write that sends the whole file in one call comes back `Tool execution aborted`. Sessions rerun the same whole write and each comes back aborted again. Never rerun the whole write after an abort. Slice the content to one small chunk with a timeout, write that chunk alone, then report the receipt with PASS.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_write.py`, and the failure class is `references/target-class.json`. Each good side writes its chunk and prints the receipt it promises.

## Slice every write

- Slice every write to one chunk with `Set-Content -LiteralPath chunk.txt -Value 'slice'` and report `slice chunk timeout PASS` [src: references/pairs.md#wa-slice]
- Write one small section with `Set-Content -LiteralPath section.txt -Value 'sec'` and report `chunk slice timeout PASS` [src: references/pairs.md#wa-chunk]

## Halve after an abort

- Halve a failing write to one chunk with `Set-Content -LiteralPath half.txt -Value 'half'` and write that chunk alone with `halve chunk timeout PASS` [src: references/pairs.md#wa-halve]
- Halve the retry with `Set-Content -LiteralPath half2.txt -Value 'half'` and write that chunk alone with `halve timeout PASS` [src: references/pairs.md#wa-half]

## One chunk, then stop

- Run one single small chunk write with `Set-Content -LiteralPath single.txt -Value 'one'` and stop after one abort with `single stop timeout PASS` [src: references/pairs.md#wa-single]
- Try one small chunk only with `Set-Content -LiteralPath once.txt -Value 'one'` then stop after the abort with `single stop report PASS` [src: references/pairs.md#wa-once]

## Stage, then append

- Stage the content first with `Set-Content -LiteralPath staged.txt -Value 'head'` then append with `Add-Content -LiteralPath staged.txt -Value 'tail'` and report `stage append timeout PASS` [src: references/pairs.md#wa-stage]
- Stage a large file with `Set-Content -LiteralPath staged2.txt -Value 'head'` slicing to one small chunk and report `stage chunk PASS` [src: references/pairs.md#wa-first]

## Background long writes

- Move a long write to the background with `Set-Content -LiteralPath receipt.txt -Value 'done'` plus a timeout, poll the receipt with `Test-Path -LiteralPath receipt.txt`, report `background receipt timeout PASS` [src: references/pairs.md#wa-back]
- Poll the receipt with `Get-Content -LiteralPath receipt2.txt -Raw` under a timeout and report `background receipt PASS` [src: references/pairs.md#wa-poll]

## Stop after the abort and report

- Close an abort with `RESULT report stop PASS` naming the chunk used [src: references/pairs.md#wa-report]
- Record the run with `RESULT record report PASS` listing the chunk used and the write result [src: references/pairs.md#wa-record]

## When a write aborts

Fix the shape once. Do not send the same whole write again. The error text names the cause: look it up in `references/errors.md`.
