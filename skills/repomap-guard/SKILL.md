---
name: repomap-guard
description: Use when a map-file read comes back missing: list the folder first, locate the file before reading, read once, then fall back and report.
version: 0.1.0
author: skillworks
tags: [maps]
license: MIT (skill text and scripts, original work)
---

# List first, read once, report the miss

A map read that guesses the path comes back `File not found: owner/name/.opencode/repomap.md`. Sessions re-read the identical missing path and each comes back missing. Never blind-read the map path. List the folder first, check the entry exists, read once only, then fall back to an existing file and close with a report.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_map.py`, and the failure class is `references/target-class.json`. Each good side prints its report with the listing plus check results.

## List before any map read

- List the folder first with `Get-ChildItem -Name` and check the entry, read once only, report with `list folder PASS checked once` [src: references/pairs.md#rm-list]
- Glob for the map name with `Get-ChildItem -Recurse -Filter repomap.md` and check the hit before any read with `glob check PASS no guess` [src: references/pairs.md#rm-glob]
- Run one single listing with `Get-ChildItem -Name | Select-Object -First 1` and stop after one miss with `single listing PASS stopped` [src: references/pairs.md#rm-single]

## Check the entry exists

- Check the entry exists with `Test-Path -LiteralPath notes.md` and report `list check exist PASS present` [src: references/pairs.md#rm-check]
- Read once only with `Get-Content -LiteralPath notes.md -Raw` then stop and report with `once stop report PASS listed` [src: references/pairs.md#rm-once]
- Close a miss with `RESULT report PASS listing` naming the listing used [src: references/pairs.md#rm-report]

## Read once, then fall back

- List first, check the entry, read once with `Get-Content -LiteralPath notes.md -TotalCount 1` and report `list check once PASS read` [src: references/pairs.md#rm-read]
- Find the file with `Get-ChildItem -Recurse -Filter *.md` and check the hit with `glob check PASS found` [src: references/pairs.md#rm-find]
- Read one existing file with `Get-Content -LiteralPath src/app.md -TotalCount 1` and report `single report PASS done` [src: references/pairs.md#rm-one]

## Stop after the miss and report

- Check once only with `Test-Path -LiteralPath repomap.md`, stop after the miss, list the folder, report `once stop PASS missed listed` [src: references/pairs.md#rm-miss]
- Fall back to the folder listing with `Get-ChildItem -Name`, read one file that exists, report `fallback list PASS existing` [src: references/pairs.md#rm-fallback]
- Record the run with `RESULT record PASS reported` listing the check used and the read result [src: references/pairs.md#rm-record]

## When a map read misses

Fix the path once. Do not reread the same missing path. The error text names the cause: look it up in `references/errors.md`.
