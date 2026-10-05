---
name: bash-allowlist
description: Use when a bash shell call comes back prevents you from using this specific tool call after a pipe or shell git reach
version: 1.0.0
author: skillworks
tags: [shell]
license: MIT (skill text and scripts, original work)
---

# One call, no pipe, dedicated tools

A shell call chained with a formatting pipe or reaching for shell git comes back `prevents you from using this specific tool call`. Run one single-purpose call with no formatting pipe, use the dedicated file tool for text, sequence single calls, and report the diff plus check results.

The full bad and good runs are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_allow.py`, and the failure class is `references/target-class.json`.

## One single call with no pipe

- Run one single call with `git status` and no formatting pipe [src: references/pairs.md#ba-single]
- Check one diff with `git diff --stat` and never apply from the shell [src: references/pairs.md#ba-status]
- Run one tool call alone and read its output directly with no `Select-Object` pipe [src: references/pairs.md#ba-nopipe]
- Run one health call with `Invoke-RestMethod` and read the body with no convert pipe [src: references/pairs.md#ba-direct]

## Dedicated tools for text

- Read text with the `Read` tool and report the lines with no shell pipe [src: references/pairs.md#ba-read]
- Make the change with the `Edit` tool and leave the tree alone otherwise [src: references/pairs.md#ba-edit]
- Search with the `Grep` tool and report matches with no shell chain [src: references/pairs.md#ba-grep]
- List files with the `Glob` tool and report the listing with no format pipe [src: references/pairs.md#ba-glob]

## Sequence single calls and report

- Sequence single calls with `Get-Content queue.txt` instead of chaining two checks [src: references/pairs.md#ba-seq]
- Check the repo first with `gh api repos` pinned ref and report the sha [src: references/pairs.md#ba-sha]
- Run one test command alone and read the log after with `Get-Content log.txt` [src: references/pairs.md#ba-log]
- Report the run with `Set-Content report.txt` listing the call, diff, checks, and PASS [src: references/pairs.md#ba-report]

## When a call is denied

Fix the shape once. Do not re-run the same denied call. The error text names the cause: look it up in `references/errors.md`.
