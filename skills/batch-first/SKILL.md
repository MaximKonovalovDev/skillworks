---
name: batch-first
description: Use when scattered GitHub calls each time out alone: batch the read-only calls into one capped dispatch with a timeout, collect the results, then write.
version: 0.1.0
author: skillworks
tags: [github]
license: MIT (skill text and scripts, original work)
---

# Batch the reads first, never scatter them

Scattered GitHub calls in owner/name each time out alone with `Request timed out` and nothing collected. One-by-one fetches, sequential content reads, and retry storms on a slow endpoint all time out the same way. Never scatter read-only calls one by one and never write before the reads land. Batch the read-only calls into one capped dispatch with a timeout, collect every result, then run the single write.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_batch.py`, and the failure class is `references/target-class.json`. Each good side batches the reads in one dispatch and prints the batch report it promises.

## Batch the reads first

- Batch scattered calls into one `batch timeout PASS capped` dispatch with a timeout [src: references/pairs.md#bf-batch]
- Cap the fan-out with a `batch cap PASS fanned` bounded dispatch, never one by one [src: references/pairs.md#bf-cap]
- Split reads before writes with a `batch read-only PASS split` reads-first order [src: references/pairs.md#bf-readonly]

## Collect with a timeout

- Pool sequential fetches as one `batch pool PASS collected` batch pool [src: references/pairs.md#bf-pool]
- Batch retry storms once with a `batch timeout PASS variants` single search batch [src: references/pairs.md#bf-search]
- Dispatch repo-record batches under a `batch timeout PASS dispatched` timeout [src: references/pairs.md#bf-timeout]

## Cover the read with a fallback

- Pair the primary with its fallback in one `batch fallback PASS primary` batch [src: references/pairs.md#bf-fallback]
- Batch multi-repo queries with a `batch cap PASS queries` cap in one dispatch [src: references/pairs.md#bf-quote]
- Hold the write until the reads land with a `batch read-only PASS writes-last` gate [src: references/pairs.md#bf-after]

## Report the batch

- Batch the API plus the raw fallback as `batch fallback PASS api-raw` together [src: references/pairs.md#bf-risk]
- Bound the slow endpoint with a `batch timeout PASS bounded` single timed call [src: references/pairs.md#bf-first]
- Close with `RESULT batch PASS collected outcomes` listing collected results and open gaps [src: references/pairs.md#bf-result]

## When a call times out

Batch the reads once. Do not scatter them again. The error text names the cause: look it up in `references/errors.md`.
