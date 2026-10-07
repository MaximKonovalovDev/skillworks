---
name: webfetch-retry
description: Use when a webfetch call comes back Request timed out: retry once with backoff and a narrower path, then fall back to the repo record or cached copy.
version: 0.1.0
author: skillworks
tags: [fetch]
license: MIT (skill text and scripts, original work)
---

# One retry with backoff, then a narrower path or fallback

A webfetch call on a slow or large page comes back `Request timed out after 30000ms`. Sessions re-issue the identical fetch back to back and each comes back timed out. Never hammer the same URL. Retry once only after a short backoff with a narrower path, cap the retries at two, then take the repo record or the cached copy.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_fetch_retry.py`, and the failure class is `references/target-class.json`. Each good side prints its report with the retry plus check results.

## Retry once after a timeout

- Retry once only with `Start-Sleep -Milliseconds 200` after a timed-out fetch, never a second retry [src: references/pairs.md#wf-retry]
- Fire the single retry only once with `retry once PASS` and stop repeating the URL [src: references/pairs.md#wf-once]
- Wait with a `backoff wait PASS` between the try and the one retry [src: references/pairs.md#wf-backoff]

## Narrow the path, never hammer

- Narrow the retry to the `narrow sub-path PASS` smallest path that answers the question [src: references/pairs.md#wf-narrow]
- Fetch a `smaller scope PASS` page instead of the full listing that timed out [src: references/pairs.md#wf-subpath]
- Enforce the `cap two PASS` retry cap and stop re-issuing the same call [src: references/pairs.md#wf-cap]

## Take the repo or cached fallback

- Switch to the `record-first verified PASS` repo record for the same owner and path [src: references/pairs.md#wf-record]
- Read the `versioned path PASS` file through the pinned ref instead of the raw host [src: references/pairs.md#wf-raw]
- Use the `cached pinned PASS` copy when the brief pins one that covers the lines [src: references/pairs.md#wf-cache]

## Stamp the timeout and report

- Stamp the miss with a `stamp timestamp PASS` timeout record carrying its timestamp [src: references/pairs.md#wf-stamp]
- Report the `paths retries PASS` attempts with retry counts and their results [src: references/pairs.md#wf-paths]
- Close with `RESULT fetch PASS` listing paths, fallback taken, and unverified gaps [src: references/pairs.md#wf-result]

## When a fetch misses

Fix the path once. Do not rerun the same slow URL. The error text names the cause: look it up in `references/errors.md`.
