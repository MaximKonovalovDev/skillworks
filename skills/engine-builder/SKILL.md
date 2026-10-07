---
name: engine-builder
description: Use when a builder run is about to report no file changes: create the packet lane and land the fix there, or verify the present work with checks and report the verified paths, instead of filing an empty report.
version: 1.1.0
author: skillworks
tags: [builder]
license: MIT
---

# Build so the run lands or claims

A builder run ends with a landed diff or with verified paths plus check lines. An empty report alone is a failed run, even when every step felt blocked. When the packet cannot proceed as written, do the next line below instead of reporting zero. The full bad and good reports are `references/pairs.md`, the machine list is `references/pairs.json`, the runner is `scripts/run_pairs.py`, and the failure class is `references/target-class.json`.

## Big slices only (no micro rows)

One existence proof is not a landed row. A row whose done-when only checks that a function exists (`typeof m.x === 'function'`, one `FOUND x` grep) with no measured number is a micro row: refuse it and build the slice that moves the number instead. Every row you land must do all three:

- Move one Scorecard row by a full point (or one buyer number by +1: views, sales, loads, adopts, gates). Paste the before and after numbers in the report. No number moved means NOOP, never DONE.
- Steal or die: name the donor repo at its pin plus the exact file and line you ported (`repo@sha path:line`), with its license. A take of shape-only with the real thing avoided is refused. Port the bytes or beat the donor on the same fixture with the same measure, and paste both numbers.
- Compare against the rival: run the closest competitor on the same input and paste both scores. We beat them on X with numbers, or the row is not DONE.

## Land-or-claim (no empty reports)

- Make the packet lane with `New-Item -ItemType Directory lane` and land the fix there with the lane flags, then report the lane diff and the PASS lines [src: references/pairs.md#eb-lane-missing]
- Keep present work untouched with `git status --short`, verify it by reading it and running the checks, then report the verified and preserved paths with the PASS lines [src: references/pairs.md#eb-present-work]
- Fix the file the audit names with `Edit <file>`, re-run the audit to PASS inside the lane, then report the diff [src: references/pairs.md#eb-audit-file]
- Read the public API and tests of `Get-Content <crate>`, land the smallest complete change with a behavior test plus one failure-case test, then wire the real consumer [src: references/pairs.md#eb-small-slice]
- Retry the locked queue with `Start-Sleep 20` and the lane FLAGS until it clears, then land the change and report the PASS lines [src: references/pairs.md#eb-cache-lock]
- Land the complete sub-slice now with `cargo test -p <crate>` and its tests, and state exactly what remains for the next packet [src: references/pairs.md#eb-sub-slice]

## Top-tier shape (every new line)

- Search first with `grep -rn <behavior> .`, reuse the shared helper in a module instead of adding a crate, and show the diff [src: references/pairs.md#eb-reuse-first]
- Model fallible input with a typed error enum carrying `Display`, use the `?` operator over `unwrap` on IO and user data, and let `expect` name the proven invariant plus a test [src: references/pairs.md#eb-typed-errors]
- Run the formatter plus the suite plus the linter with `cargo fmt -p <crate>` and the lane FLAGS, then paste the RESULT lines into the report with zero regressions [src: references/pairs.md#eb-check-trio]
- Keep the hot path free of per-tick allocation with `reused buffers` owned by the caller and slices in and out, and prove it with the allocation probe measured over the tick body [src: references/pairs.md#eb-hot-path]
- Add a small dependency behind a `feature` flag so it passes the deny check, and record the dependencies doc row in the docs [src: references/pairs.md#eb-dep-flag]
- Report the changed paths with `git diff --stat`, the commands with their results, and what is still unverified in one closing block [src: references/pairs.md#eb-report]
