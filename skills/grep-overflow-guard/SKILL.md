---
name: grep-overflow-guard
description: Use when a Grep call over the whole tree fails with Ripgrep JSON record exceeded N bytes (wide scope, unfiltered search, no glob, one call over many folders, unbounded hits, broad regex): narrow to one folder, add a file-type filter, and rerun chunked, then report with PASS.
version: 0.1.0
author: skillworks
tags: [search]
license: MIT (skill text and scripts, original work)
---

# Narrow first, rerun chunked, report the sweep

A `Grep` call over the whole tree comes back `Ripgrep JSON record exceeded N bytes` with nothing searched. Sessions rerun the same wide search and each comes back overflowed again. Never rerun the whole-tree search after an overflow. Narrow the scope to one folder first, add a file-type filter, rerun chunked folder by folder, merge the hits, then report the sweep with PASS.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_grep.py`, and the failure class is `references/target-class.json`. Each good side narrows first and prints the chunked report it promises.

## Narrow the scope first

- Narrow a whole-tree miss to one folder with `Grep pattern docs` searched first, rerun chunked, and report `narrow scope chunked search PASS` [src: references/pairs.md#gl8-b01]
- Narrow a whole-repo miss with a glob with `Grep pattern glob *.md` first, rerun in two chunks, and report `glob narrow rerun PASS` [src: references/pairs.md#gl8-b03]
- Narrow to skills after a miss with `Grep pattern skills` first, rerun chunked, and report `narrow rerun PASS skills path` [src: references/pairs.md#gl8-g02]

## Filter before the rerun

- Add a file-type filter with `Grep pattern include *.md` first, rerun the search, and report `file-type filter rerun PASS` [src: references/pairs.md#gl8-b02]
- Switch a broad regex to an exact literal with `Grep literal helper` first, rerun chunked, and report `exact literal rerun PASS` [src: references/pairs.md#gl8-b06]
- Use a glob plus a type filter with `Grep pattern glob include` chunked, and report `glob type filter PASS lines` [src: references/pairs.md#gl8-g03]

## Split into chunks and merge

- Split an 8-repo miss by folder with `Grep pattern folder` per chunk, merge the hits, and report `split folders merge PASS` [src: references/pairs.md#gl8-b04]
- Limit the hits with `Grep pattern head` first, page through chunks, and report `limit hits head PASS` [src: references/pairs.md#gl8-b05]
- Split the count by folder with `Grep pattern callers` per chunk, merge the results, and report `split merge PASS count` [src: references/pairs.md#gl8-g04]

## Report the sweep

- Scope to docs with `Grep pattern docs filter` by type, run chunked, and report `scope filter chunked PASS path` [src: references/pairs.md#gl8-g01]
- Search the exact literal with `Grep literal writer` chunked, and report `literal chunked PASS file` [src: references/pairs.md#gl8-g05]
- Report the sweep with `Grep pattern merged` listing chunk results, and close `results chunks unverified PASS` [src: references/pairs.md#gl8-g06]

## When the grep overflows

Fix the scope once. Never rerun the same whole-tree search after an overflow. The error text names the cause: look it up in `references/errors.md`.
