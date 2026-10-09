---
name: task-scope
description: Use when fanning out parallel subagent task runs: claim one item per run, join each batch before the next
version: 1.2.0
author: skillworks
tags: [orchestration]
license: MIT (skill text and scripts, original work)
---

# Scope one task run at a time

A lead or orchestrator fans out parallel subagent task calls. Stragglers, duplicates of claimed items, and runs past the round stop line come back `Task cancelled`. Claim one item per run, sequence dispatches, bound fan-out with join, slice long work with per-slice receipts, and check round eligibility before dispatch.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_scope.py`, and the failure class is `references/target-class.json`.

## Claim before dispatch (no duplicate cancels)

- Claim one item with `Set-Content claims.txt` before dispatch so the run is unique [src: references/pairs.md#ts-claim]
- Read the claims file with `Get-Content claims.txt` and skip anything claimed in the last 2 h [src: references/pairs.md#ts-duplicate]
- List running runs with `Get-Content running.txt` first and never re-dispatch live work [src: references/pairs.md#ts-running]
- Check round state with `Get-Content round.txt` and dispatch only when the lane token names new work [src: references/pairs.md#ts-eligible]
- Never dispatch the same description twice in one session with `Set-Content claims.txt`: check the claims file for already-dispatched descriptions, not just queue items [src: references/pairs.md#ts-dupdesc]
- Record every dispatched description with `Set-Content claims.txt` and skip it when it appears again [src: references/pairs.md#ts-descclaim]
- Sequence a retry in a fresh lane with `Set-Content claims.txt` claiming the lane before the retry so the straggler is not cancelled [src: references/pairs.md#ts-retryseq]
- Dedupe research topics with `Set-Content claims.txt` recording the first topic and skipping the duplicate [src: references/pairs.md#ts-topicdedupe]
- Never dispatch a vague single token with `Set-Content claims.txt`: write one item before dispatch [src: references/pairs.md#ts-vagueclaim]

## Bound the fan-out (no straggler cancels)

- Keep the batch bounded with `1..3` and join each batch before the next [src: references/pairs.md#ts-fanout]
- Claim one queue item with `Select-Object -First 1` then sequence the rest [src: references/pairs.md#ts-single]
- Pick the next item with `Get-Content queue.txt` after skipping claimed ones [src: references/pairs.md#ts-pick]
- Run a small batch with `ForEach-Object` bounded and join it before the next batch [src: references/pairs.md#ts-batch]
- Fan out parallel runs with `Select-Object -First 1` claiming one item per run and join before the next batch [src: references/pairs.md#ts-onefan]
- Fire a land batch with `ForEach-Object` bounded to three and join it before the next batch [src: references/pairs.md#ts-landbatch]
- Sequence an orchestrator fan-out with `Select-Object -First 1` claiming one item then the rest in order [src: references/pairs.md#ts-orchseq]
- Cap parallel captures with `1..3` and join before the next batch [src: references/pairs.md#ts-capbound]

## Slice long work (no lost cancels)

- Cut long work with `Set-Content slice1.txt` writing one receipt per slice [src: references/pairs.md#ts-slice]
- Resume a long repair with `Get-Content slice2.txt` reading the last receipt first [src: references/pairs.md#ts-resume]
- Make reruns idempotent with `Set-Content rerun.txt` so a resume gives the same result [src: references/pairs.md#ts-idempotent]
- Report the run with `Set-Content report.txt` listing claim, output, RESULT line, and unverified gaps [src: references/pairs.md#ts-report]
- Chain repairs with `Set-Content slice3.txt` writing one receipt per fix and resuming from it [src: references/pairs.md#ts-repairchain]

## When a run is cancelled

Fix the scope once. Do not send the same dispatch again. The error text names the cause: look it up in `references/errors.md`.
