---
name: brief-gate
description: Use when a pilot dispatch reads a lead brief file that does not exist: write the one-page brief first with goal plus scope plus proof plus stop, gate the dispatch on the brief file, then report PASS.
version: 0.1.0
author: skillworks
tags: [pilot]
license: MIT (skill text and scripts, original work)
---

# Gate every pilot dispatch on a written brief

A pilot dispatched against an owner/name brief that was never written reads lead2.md which does not exist and comes back `File not found` with a guessed path. Oral handoffs and one-line briefs send the next wave at stale files. Never dispatch a pilot on a missing, vague, or oral brief. Write the one-page brief first with goal plus scope plus proof plus stop, gate every dispatch on the brief file existing, and report PASS.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_brief.py`, and the failure class is `references/target-class.json`. Each good side reads only the written brief and prints the gated report it promises.

## Write the brief first

- Write the one-page `brief plan PASS written first` brief before any pilot dispatch [src: references/pairs.md#bg-write]
- Shape every brief into `brief sections PASS goal scope proof stop` goal plus scope plus proof plus stop sections [src: references/pairs.md#bg-sections]
- Convert each oral handoff into a `brief handoff PASS written filed` written brief file [src: references/pairs.md#bg-handoff]
- Open every pilot run with a `brief plan PASS dispatched written` written plan, never a guess [src: references/pairs.md#bg-plan]

## Gate every dispatch on the brief

- Hold each dispatch on the `brief gate PASS held then released` brief-file gate until the brief exists [src: references/pairs.md#bg-gate]
- Approve the `brief approval PASS approved released` brief before releasing the dispatch wave [src: references/pairs.md#bg-approval]
- Gate each build on the `brief gate PASS build released` brief file, then release it [src: references/pairs.md#bg-build]

## Verify the file before dispatch

- Check the brief file with a `brief verify PASS exists dispatched` existence check before dispatch [src: references/pairs.md#bg-verify]
- Shape each handoff into `brief sections PASS shaped goal scope proof stop` goal plus scope plus proof plus stop [src: references/pairs.md#bg-shape]
- Recheck the queue with a `brief verify PASS checked dispatched` file check before the next dispatch [src: references/pairs.md#bg-check]
- File each cross-repo handoff as a `brief handoff PASS filed written` brief file before dispatch [src: references/pairs.md#bg-file]

## Report the brief

- Close the wave with `RESULT brief PASS approval recorded` listing brief, approval, and dispatch [src: references/pairs.md#bg-result]

## When a pilot misses

Write the brief once. Do not redispatch on a guess. The error text names the cause: look it up in `references/errors.md`.
