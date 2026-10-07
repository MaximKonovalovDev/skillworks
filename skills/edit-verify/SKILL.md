---
name: edit-verify
description: Use when an edit lands but nothing proves it: re-read the edited lines, run the lint check, and report the diff plus checks before closing.
version: 0.3.0
author: skillworks
tags: [editor, verify]
license: MIT
---

# Verify after the edit, then lint, then report

An edit that reports success but is never re-read stays red: a stale
follow-up throws Could not find oldString, a close with no lint ships a
red file, and a report with no diff proves nothing. Re-read the edited
lines, run the lint, read the diff, then report. The full bad and good
runs are `references/pairs.md`, the machine list is
`references/pairs.json`, the runner is `scripts/run_verify.py`, and the
failure class is `references/target-class.json`.

## Verify after the edit (prove it is on disk)

- Re-read the edited lines with `Read <file>` right after every `Edit <file>` and confirm the new text is on disk with verified plus PASS [src: references/pairs.md#ev-reread]
- Quote six lines from the fresh `Read <file>` output with `Get-Content -LiteralPath <file>` before any follow-up edit on the same file [src: references/pairs.md#ev-quote]
- Check the line endings with `Get-Content -Raw <file>` after the edit: CRLF stays CRLF and LF stays LF [src: references/pairs.md#ev-endings]
- Read the diff hunks with `git diff <file>` plus `git diff --stat` before closing and confirm the single intended change [src: references/pairs.md#ev-diff]
- Refuse the no-op with `Get-Content <file>`: identical oldString and newString means verify the file already holds the wanted text [src: references/pairs.md#ev-noop]
- Count first with `(Select-String -Pattern <old> <file>).Count` and land a single change only, never force a short match [src: references/pairs.md#ev-single]
- Match tabs vs spaces with ``Select-String -Pattern "`t" <file>`` and copy the exact indent into oldString [src: references/pairs.md#ev-tabs]
- Keep trailing whitespace exact with `Get-Content -Raw <file>` and never trim the oldString [src: references/pairs.md#ev-trail]
- Re-read after any outside write with `Get-Content -LiteralPath <file>` when the file may have changed since the last read [src: references/pairs.md#ev-stale]
- Widen a short hit with six surrounding lines from `Get-Content <file>` until the match is one place [src: references/pairs.md#ev-widen]
- Match case exactly with `Select-String -Pattern <old> <file>` and never change the case of oldString [src: references/pairs.md#ev-case]
- Strip the BOM with `Get-Content -Raw <file>` and match `line one` before landing the oldString [src: references/pairs.md#ev-bom]
- Scope long lines with `(Get-Content <file>).Count` and keep the oldString inside the read window [src: references/pairs.md#ev-long]
- Match literally with `Select-String -SimpleMatch <file>` and never read regex chars as patterns [src: references/pairs.md#ev-regex]
- Keep the final newline with `Get-Content -Raw <file>` and never drop the closing line ending [src: references/pairs.md#ev-eol]
- Quote backtick spans with `'quoted'` in `target.txt` and widen until the match is one place [src: references/pairs.md#ev-backtick]

## Lint after the edit (close green, never red)

- Run the lint with `python -m pytest tests/test_<name>.py -q` after every code edit and never close while the check is red [src: references/pairs.md#ev-lint]
- Re-run the check with `python -m pytest tests/ -q` after each fix until it is green, then report [src: references/pairs.md#ev-rerun]
- Paste the real error line from the failed check beside the `python skills/edit-verify/scripts/run_verify.py` evidence, never paraphrase the failure [src: references/pairs.md#ev-error]
- Run the pair proof with `python skills/edit-verify/scripts/run_verify.py` before claiming the class is fixed [src: scripts/run_verify.py#live-check]
- Close with the changed paths from `git diff --stat`, the check commands with their results, and what is still unverified [src: references/pairs.md#ev-report]
- Ship no scaffold text: every rule in `SKILL.md` carries its source and the body holds only verified rules [src: references/pairs.md#ev-noscaffold]
