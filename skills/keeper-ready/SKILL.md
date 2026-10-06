---
name: keeper-ready
description: Use when a task dispatch comes back Keeper readiness hold with no unclaimed ready work or changed evidence: check the queue first, list unclaimed ready work, verify changed evidence, dispatch once only when work exists, then report with PASS.
version: 0.1.0
author: skillworks
tags: [queue]
license: MIT
---

# Check the queue first, dispatch once, report the hold

A task dispatch that skips the queue comes back `Keeper readiness hold: no unclaimed ready work or changed evidence`. Sessions dispatch again the same way and each comes back hold again. Never blind-dispatch into the queue. Check the queue first, list unclaimed ready work, verify changed evidence, dispatch once only when work exists, then report with PASS plus a RESULT line.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_keeper.py`, and the failure class is `references/target-class.json`. Each good side prints its report with the listing plus check results.

## Check the queue first

- List the queue first with `Get-ChildItem -Name` and check unclaimed ready work, dispatch once only when work exists and report `queue unclaimed PASS ready listed` [src: references/pairs.md#kr-queue]
- Run one single listing with `Get-ChildItem -Name | Select-Object -First 1` and stop after the hold with `single listing PASS stopped once` [src: references/pairs.md#kr-single]
- Try once only with `Get-Content -LiteralPath queue.txt -Raw` then stop after the hold and list the queue with `once stop PASS listed hold` [src: references/pairs.md#kr-once]

## Verify changed evidence

- Verify changed evidence with `Get-Content -LiteralPath evidence.txt -TotalCount 1` and dispatch once only on changed evidence with `evidence changed PASS verified once` [src: references/pairs.md#kr-evidence]
- Verify the evidence file with `Get-Content -LiteralPath evidence.txt -Raw` and report the change with `evidence verify PASS changed once` [src: references/pairs.md#kr-verify]
- Check the queue with `Get-ChildItem -Name` plus read once with `Get-Content -LiteralPath notes.md -TotalCount 1` and report `queue check PASS listed once` [src: references/pairs.md#kr-check]

## Seat only when eligible

- Check eligible work with `Test-Path -LiteralPath queue.txt` and dispatch once only when eligible work exists with `eligible check PASS listed once` [src: references/pairs.md#kr-eligible]
- List eligible work with `Get-ChildItem -Recurse -Filter *.txt` and report the seat with `eligible list PASS seated once` [src: references/pairs.md#kr-list]
- Stop after the miss with `Test-Path -LiteralPath seat.txt` then list the folder and report `seat stop PASS listed once` [src: references/pairs.md#kr-seat]

## Stop after the hold and report

- Fall back to changed evidence with `Get-ChildItem -Name` plus `Get-Content -LiteralPath evidence.txt -TotalCount 1` and report `changed fallback PASS listed once` [src: references/pairs.md#kr-fallback]
- Close a hold with `RESULT report PASS listing` naming the listing used [src: references/pairs.md#kr-report]
- Record the run with `RESULT record PASS reported` listing the check used and the dispatch result [src: references/pairs.md#kr-record]

## When a dispatch holds

Fix the cause once. Do not send the same dispatch again. The error text names the cause: look it up in `references/errors.md`.
