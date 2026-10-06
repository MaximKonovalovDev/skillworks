---
name: websearch-retry
description: Use when a websearch call comes back backend busy, missing result field, or timed out: retry once with backoff and a narrower query, then fall back.
version: 0.1.0
author: skillworks
tags: [search]
license: MIT (skill text and scripts, original work)
---

# One retry with backoff, then fall back

A websearch call that hits a busy backend comes back `StatusCode: non 2xx status code`, a call that reads a wrong shape comes back `Missing key at ["result"]`, and a wide call comes back `web_search_exa request timed out`. Sessions repeat the identical query back to back and each comes back busy. Never hammer the same wording. Retry once only after a short backoff with a narrower query, guard the result shape, bound the wait, then use another search path.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_search.py`, and the failure class is `references/target-class.json`. Each good side prints its report with the retry plus check results.

## Retry once after a busy backend

- Retry once only with `Start-Sleep -Milliseconds 200` after a backend busy status, never a second retry [src: references/pairs.md#ws-retry]
- Fire the single retry only once with `retry once PASS` and stop repeating the wording [src: references/pairs.md#ws-once]
- Wait with a `backoff once PASS` between the try and the one retry [src: references/pairs.md#ws-backoff]

## Narrow the query, never hammer

- Narrow the retry with `fewer words PASS` using fewer words and a smaller scope [src: references/pairs.md#ws-narrow]
- Run one single query with `single query PASS` and never chain searches in a row [src: references/pairs.md#ws-single]
- Take the fallback path with `fallback retry PASS` after the one retry misses [src: references/pairs.md#ws-fallback]

## Guard the result shape

- Guard the shape first with `guard result field PASS` checking the result field exists [src: references/pairs.md#ws-guard]
- Read only the checked shape with `shape change PASS` after the guard passes [src: references/pairs.md#ws-shape]
- Change the query shape with `change shape guard PASS` instead of repeating the failing call [src: references/pairs.md#ws-change]

## Bound the wait and report

- Bound the wait with `bound single PASS` keeping one single query inside a short wait [src: references/pairs.md#ws-bound]
- Cap a wide scope with `bound wait backoff PASS` instead of waiting without a bound [src: references/pairs.md#ws-timeout]
- Report the run with `RESULT retry PASS` listing query shape, retry used, and unverified gaps [src: references/pairs.md#ws-report]

## When a search misses

Fix the shape once. Do not rerun the same long query. The error text names the cause: look it up in `references/errors.md`.
