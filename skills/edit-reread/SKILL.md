---
name: edit-reread
description: Use when an Edit reports Could not find oldString or multiple matches: re-read the exact lines first and land a unique match instead of guessing oldString from memory.
version: 1.0.0
author: skillworks
tags: [editor]
license: MIT (skill text and scripts), CC-BY-4.0 (PowerShell-Docs text), MIT (PowerShell-Docs code samples)
---

# Re-read before every edit

Stale or guessed oldString fails exactly: line endings, tabs, trailing spaces, or a file that changed after the last Read. A short oldString matches in several places. Copy oldString from a fresh Read, match the bytes exactly, widen until unique, then report the diff and checks. The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_pairs.py`, and the failure class is `references/target-class.json`.

## Reread-first (no stale or guessed edits)

- Read the exact lines with `Read <file>` immediately before every `Edit <file>`, and copy oldString from the Read output verbatim [src: references/pairs.md#er-read-first]
- Check the line endings first with `Get-Content -Raw <file>`, match CRLF or LF exactly in oldString, never mix them [src: references/pairs.md#er-crlf]
- Match tabs exactly with `Select-String -Pattern "\t" <file>`, never retype tabs as spaces [src: references/pairs.md#er-tabs]
- Keep trailing whitespace with `Get-Content -Raw <file>`, include every trailing space in oldString [src: references/pairs.md#er-trailing]
- Re-read after any other session writes with `Read <file>`, use the fresh text as oldString when the first Read is stale [src: references/pairs.md#er-stale]
- Never type oldString from memory with `Read <file>`, the Read output is the only source for oldString [src: references/pairs.md#er-memory]

## Unique-match (no ambiguous edits)

- Widen short matches with `Read <file>` plus three surrounding lines above and below until the match is unique [src: references/pairs.md#er-unique]
- Count occurrences first with `(Select-String -Pattern <old> <file>).Count`, refuse the single edit while the count is above one [src: references/pairs.md#er-count]
- Anchor on a unique neighbor with `Read <file>`, include the neighbor lines so oldString matches exactly one place [src: references/pairs.md#er-anchor]
- Use `replaceAll` only with the verified count from `(Select-String -Pattern <old> <file>).Count` in the report [src: references/pairs.md#er-replace-all]
- Refuse identical oldString and newString with `Get-Content <file>`, verify the file already holds the wanted text instead [src: references/pairs.md#er-noop]
- Report the changed paths with `git diff --stat`, the check commands with their results, and what is still unverified [src: references/pairs.md#er-report]
