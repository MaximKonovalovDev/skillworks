---
name: edit-unique
description: Use when an Edit reports Found multiple matches for oldString: refuse the blind edit, re-read wider until the match is unique or count first and replaceAll with the verified count, retry once then stop (repeated import block in three places, one-line export in two modules).
version: 1.2.0
author: skillworks
tags: [editor]
license: MIT (skill text and scripts, original work)
---

# Land a unique match

A short oldString matches in several places and the tool reports Found multiple matches for oldString. Never guess from memory and never land the blind edit: refuse the ambiguous single edit, re-read with wider surrounding lines and retry once, and a second identical failure ends the step as partial. Count first and use replaceAll only with the verified count when every occurrence must change. The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_unique.py`, and the failure class is `references/target-class.json`.

## Widen until unique (no ambiguous edits)

- Widen a lone brace with `Read <file>` plus three surrounding lines above and below until the match is unique [src: references/pairs.md#eu-brace]
- Anchor a repeated status line on its card title with `Read <file>`, include the title so oldString matches exactly one place [src: references/pairs.md#eu-status]
- Include the row id lines with `Read <file>` when oldString is a board table fragment in two rows [src: references/pairs.md#eu-board]
- Include the section body with `Read <file>` when oldString is a heading repeated in three places [src: references/pairs.md#eu-heading]
- Include the surrounding block lines with `Read <file>` when oldString is a one-line import in two blocks [src: references/pairs.md#eu-import]
- Re-read a copied sentence with wider surrounding lines with `Read <file>` so the match is unique [src: references/pairs.md#eu-sentence]

## Count, anchor, report (no blind single edit)

- Change a repeated block with `Read <file>` including enough surrounding lines that the match is unique [src: references/pairs.md#eu-unique]
- Re-read wider with `Read <file>` after the first attempt reports more than one match, then apply the change [src: references/pairs.md#eu-reread]
- Count first with `(Select-String -Pattern <old> <file>).Count`, use `replaceAll` only with that verified count in the report [src: references/pairs.md#eu-replaceall]
- Refuse the ambiguous single edit with `(Select-String -Pattern <old> <file>).Count` while the count is above one, then make the match unique [src: references/pairs.md#eu-count]
- Anchor on a unique neighbor line with `Read <file>`, include the neighbor so oldString matches exactly one place [src: references/pairs.md#eu-anchor]
- Report the changed paths with `git diff --stat`, the check commands with their results, and what is still unverified [src: references/pairs.md#eu-report]
