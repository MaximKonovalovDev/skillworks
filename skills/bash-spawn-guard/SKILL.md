---
name: bash-spawn-guard
description: Use when a long shell call, suites run, detached launch, or chained checks might hit Unknown ChildProcess.kill
version: 1.4.0
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

## Dispatch before the kill

- Never chain with `;` run `one command timeout limit` only [src: references/pairs.md#bs-chain4]
- Never poll `Start-Process -PassThru` with `Start-Sleep` use `Wait-Process timeout receipt` plus poll [src: references/pairs.md#bs-clone]
- Never double-poll a `Start-Process shim` with `Start-Sleep 3` use `bounded wait receipt` plus poll [src: references/pairs.md#bs-shim]
- Never chain `detect checks redirects` piped to tail run `single check file timeout` alone [src: references/pairs.md#bs-detect]
- Never run `npm run suites` bare run `one file timeout limit` from a file [src: references/pairs.md#bs-suites]
- Never sleep-poll a `Start-Sleep 45 redeploy` with no receipt use `bounded wait receipt` plus poll [src: references/pairs.md#bs-redeploy]
- Never run a full `cargo test heavy` in one call run `slice one chunk timeout` alone [src: references/pairs.md#bs-cargo]
- Never double-run `node test full` piped with no slice run `single file timeout` alone [src: references/pairs.md#bs-nodetest]
- Never chain `triple detect plus board` grep in one call run `single check file timeout` alone [src: references/pairs.md#bs-detect3]
- Never chain `proof plus check` scans in one call run `single check timeout` alone [src: references/pairs.md#bs-proofchain]
- Never chain `git status log score` in one call run `single check timeout` alone [src: references/pairs.md#bs-gitstat]
- Never run full `python pytest` in one call run `slice one chunk timeout` alone [src: references/pairs.md#bs-pytest]
- Never run verbose `npm install` foreground use `background receipt timeout` plus poll [src: references/pairs.md#bs-npminstall]
- Never `Start-Sleep poll log` with no timeout use `bounded wait receipt` plus poll [src: references/pairs.md#bs-logpoll]
- Never run long `Get-Content pipe tail` in one call run `file timeout limit` from a file [src: references/pairs.md#bs-longpipe]
- Never run piped `cargo test pipe tail` in one call run `slice one chunk file timeout` alone [src: references/pairs.md#bs-cargopipe]
- Never chain `status batch board` reads in one call run `single check timeout` alone [src: references/pairs.md#bs-batchchain]
- Never chain `lock diff listing` reads in one call run `single check file timeout` alone [src: references/pairs.md#bs-lockchain]
- Never run bare `node rome-score` with exit check run `single file timeout` alone [src: references/pairs.md#bs-romescore]
- Never chain `fleet scan loads` in one call run `single check timeout` alone [src: references/pairs.md#bs-scanchain]

## When a call is killed

Fix the shape once. Do not rerun the same long foreground call. The error text names the cause: look it up in `references/errors.md`.
