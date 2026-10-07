---
name: ready-file-check
description: Use when a read call comes back File not found on a missing queue path (ready, claims, lead-lock, review, inbox, or packet path)
version: 1.1.0
author: skillworks
tags: [queue]
license: MIT (skill text and scripts, original work)
---

# List first, never guess a ready path

A pilot, lead, judge, planner, or builder seat reads a hardcoded queue path - a
ready file, claims file, lead-lock file, review file, inbox file, or packet
path - after the keeper moved or consumed it, and the read comes back
`File not found`. List the ready folder first, read only files that exist,
follow the batch doc for the live packets, take only named items, skip misses
gracefully, and report the diff plus check results.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_ready.py`, and the failure class is `references/target-class.json`.

## List the folder first

- List the folder first with `Get-ChildItem ready` and read only what the listing shows [src: references/pairs.md#rf-list]
- Read the batch doc with `Get-Content batch.md` and take only the packet it names [src: references/pairs.md#rf-batch]
- Read what exists with `Get-Content target.txt` after the listing, never a remembered path [src: references/pairs.md#rf-exists]
- Check the done folder with `Get-Content done` and skip what is already consumed [src: references/pairs.md#rf-done]

## Follow the batch doc

- Handle the miss with `Get-Content batch.md` listing the current packets when the file is gone [src: references/pairs.md#rf-offset]
- Check existence first with `Test-Path target.txt` so a loop never crashes on a miss [src: references/pairs.md#rf-loop]
- List the ready folder with `Get-ChildItem ready` and report the packets the batch doc names [src: references/pairs.md#rf-start]
- Skip claimed items with `Get-Content claims.txt` and sequence one eligible item [src: references/pairs.md#rf-pick]

## Check existence and report

- Report the listing with `Get-Content target.txt` quoting the found items and the diff [src: references/pairs.md#rf-state]
- Resume with `Get-Content batch.md` skipping consumed packets and taking the next one [src: references/pairs.md#rf-resume]
- Sweep gracefully with `Test-Path target.txt` checking each path before reading it [src: references/pairs.md#rf-sweep]
- Report the run with `Set-Content report.txt` listing the item, diff, checks, and PASS [src: references/pairs.md#rf-report]

## When a read misses

Fix the shape once. Do not re-read the same gone file. The error text names the cause: look it up in `references/errors.md`.
