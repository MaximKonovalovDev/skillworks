---
name: task-abort-guard
description: Use when a task write read edit or grep call comes back Tool execution aborted after a long run
version: 1.1.0
author: skillworks
tags: [queue]
license: MIT (skill text and scripts, original work)
---

# One small call with a timeout

A non-bash tool call that runs long or fans out comes back `Tool execution aborted`. Dispatch one task alone with a timeout, slice writes reads and edits into one small chunk, narrow every search, move long waits to background with a receipt poll, and report the diff plus check results.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_task.py`, and the failure class is `references/target-class.json`.

## Dispatch one task at a time

- Dispatch one task with `task one deliverable timeout` and wait with a bound before the next [src: references/pairs.md#ta-dispatch]
- Sequence the rest with `task sequence one alone` running one call alone with a timeout [src: references/pairs.md#ta-sequence]
- Wait in background with `Start-Job timeout` instead of a foreground wait with no bound [src: references/pairs.md#ta-background]
- Poll a receipt with `Get-Content receipt.txt` on a short loop with a timeout [src: references/pairs.md#ta-receipt]

## Slice into one small chunk

- Slice a write with `Set-Content chunk.txt` writing one small chunk with a timeout [src: references/pairs.md#ta-write]
- Limit a read with `Get-Content target.txt` to a few lines with a small offset window [src: references/pairs.md#ta-read]
- Re-read before an edit with `Read section exact` then change one small hunk only [src: references/pairs.md#ta-edit]
- Narrow a search with `Grep folder pattern` in one folder with a file pattern and a timeout [src: references/pairs.md#ta-narrow]

## Limit plus report

- Slice the work with `slice one chunk timeout` so each run handles a single piece [src: references/pairs.md#ta-slice]
- Limit the output with `limit read timeout` keeping every call to a few lines [src: references/pairs.md#ta-limit]
- Run one chunk with `small chunk edit timeout` and report the diff plus check results [src: references/pairs.md#ta-chunk]
- Report the run with `Set-Content report.txt` listing timeout, slice, receipt, and PASS [src: references/pairs.md#ta-report]

## New shapes from 48 h scan

- Dispatch a parallel build with `task timeout single` running one task alone with a timeout [src: references/pairs.md#ta-task-timeout]
- Write with `Set-Content receipt.txt` one chunk plus receipt on a short timeout [src: references/pairs.md#ta-write-receipt]
- Read with `Get-Content target.txt` a one-line window plus offset timeout [src: references/pairs.md#ta-read-window]
- Edit stale text after `Read section exact` reread with a timeout [src: references/pairs.md#ta-edit-reread]
- Search with `Grep folder pattern` scoped to one folder with a timeout [src: references/pairs.md#ta-grep-scope]

## When a call aborts

Fix the shape once. Do not rerun the same long or parallel call. The error text names the cause: look it up in `references/errors.md`.
