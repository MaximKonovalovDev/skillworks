---
name: repro-first
description: Use when a task dispatch comes back Tool execution aborted: run one small bounded repro first with a timeout, quote it, then dispatch the fix.
version: 0.1.0
author: skillworks
tags: [task]
license: MIT (skill text and scripts, original work)
---

# One bounded repro before any task dispatch

A long foreground task call comes back `Tool execution aborted` with no repro on record. Whole-task redispatches abort again after minutes with nothing learned. Never redispatch the same unreproduced step. Run one small bounded repro first with a timeout, quote its output, then dispatch the fix.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_repro.py`, and the failure class is `references/target-class.json`. Each good side prints its report with the repro plus check results.

## Repro the step first

- Run one `repro timeout PASS` bounded repro with a timeout before any dispatch [src: references/pairs.md#rp-repro]
- Cut the abort to the `slice single step PASS` failing step run alone, never the whole call [src: references/pairs.md#rp-slice]
- Quote the exact error with a `repro before PASS` run before the fix [src: references/pairs.md#rp-before]

## Stop blind redispatch

- Halt the second identical call with `stop redispatch PASS` and repro under a timeout [src: references/pairs.md#rp-stop]
- Shrink the kitchen-sink call to the `minimal one failure PASS` single failure [src: references/pairs.md#rp-minimal]
- Bound the builder report with a `repro timeout PASS` timed run and its output [src: references/pairs.md#rp-timeout]

## Verify before and after

- Show the failing run first with `repro before PASS` output on record [src: references/pairs.md#rp-quote]
- Prove the fix with `repro verify PASS` failing-before and passing-after outputs [src: references/pairs.md#rp-verify]
- Close the proposal with the `repro after PASS` passing run quoted [src: references/pairs.md#rp-after]

## Report the repro

- Repro the riskiest step alone first with `risk slice PASS` output [src: references/pairs.md#rp-risk]
- Isolate the first symptom with `first symptom PASS` output alone [src: references/pairs.md#rp-first]
- Close with `RESULT repro PASS` listing outcomes, fix dispatched, and open gaps [src: references/pairs.md#rp-result]

## When a task aborts

Repro one step once. Do not redispatch the same call. The error text names the cause: look it up in `references/errors.md`.
