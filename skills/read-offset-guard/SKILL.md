---
name: read-offset-guard
description: Use when reading a file with offset and limit, and when a read call comes back Offset N is out of range for this file
version: 1.2.0
author: skillworks
tags: [read]
license: MIT (skill text and scripts, original work)
---

# Count first, clamp every offset

A read with a guessed offset comes back `Offset N is out of range for this
file (M lines)`. The remembered length was stale or the file shrank. Never
retry the same offset. Count the lines first, short-circuit an empty file,
clamp every offset into [0, lines-1], step by the limit, treat one-past-the-end
as a tail read, and report the lines with the diff and check results.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_offset.py`, and the failure class is `references/target-class.json`. Each good side prints its report with the diff plus check results.

## Count the lines first

- Count the lines first with `(Get-Content target.txt).Count` and never trust a remembered length [src: references/pairs.md#ro-count]
- Re-check the current length with `(Get-Content target.txt).Count` before reusing an old offset [src: references/pairs.md#ro-stale]
- Learn the length from the head with `Get-Content target.txt -TotalCount 3` before any jump [src: references/pairs.md#ro-jump]
- Always pass a small limit with `Select-Object -First 3` on every read [src: references/pairs.md#ro-nolimit]
- Short-circuit an empty file with `if ($n -eq 0)` reporting 0 lines and never clamping into [0, -1] [src: references/pairs.md#ro-empty0]
- Re-check a board near 133 lines with `(Get-Content target.txt).Count` before jumping past 130 [src: references/pairs.md#ro-board180]

## Clamp every offset and step

- Clamp every offset with `[Math]::Min(offset, lines - 1)` into [0, lines-1] [src: references/pairs.md#ro-overshoot]
- Shrink the limit at the end with `[Math]::Min($l, $n - $o)` so the last read stops at the last line [src: references/pairs.md#ro-queue32]
- Read one section with `Select-Object -Skip $o -First $l` keeping the offset inside the length [src: references/pairs.md#ro-head]
- Start at the first line with `Select-Object -Skip 0 -First 3` for the head [src: references/pairs.md#ro-first]
- Step forward by the limit with `$o += $l` and stop at the last line [src: references/pairs.md#ro-walk]
- Re-check a long index near 544 lines with `(Get-Content target.txt).Count` before jumping to 600 [src: references/pairs.md#ro-index544]
- Re-check a long index near 534 lines with `(Get-Content target.txt).Count` before jumping to 600 [src: references/pairs.md#ro-index534]

## Tail the end and report

- Treat one-past-the-end as tail with `Get-Content target.txt -Tail 2` instead of erroring [src: references/pairs.md#ro-past-end]
- Read the end with `Get-Content target.txt -Tail 2` clamped to the last lines [src: references/pairs.md#ro-tail]
- Count the lines again with `(Get-Content target.txt).Count` after the file changes [src: references/pairs.md#ro-recount]
- Report the read with `Set-Content report.txt` listing path, offset, limit, RESULT, and PASS [src: references/pairs.md#ro-report]
- Tail a board end near 133 lines with `Get-Content target.txt -Tail 2` instead of erroring past 130 [src: references/pairs.md#ro-handoff135]

## When a read overshoots

Fix the shape once. Do not re-read the same past-the-end offset. The error text names the cause: look it up in `references/errors.md`.
