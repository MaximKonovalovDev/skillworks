---
role: runner
title: K-06 audit before/after seconds pair (export-dupes effect)
---

Goal: Produce the missing K-06 before/after pair (or prove none exists): time `python -m book2skill audit --skill <dir>` TWICE on TEMP copies of skills/progit-branching — (a) WITH 4-target export-like dupe dirs added, (b) WITHOUT (canonical, post-K-26 skip). 3 runs each, median seconds. Then write the pair into sprint/board.md K-06 Evidence: either "audit X.XXs (30 files, pre-skip walk) -> Y.YYs (8 files, K-26 skip 2b85759)" if Y<X, or "no seconds win (I/O floor), keep READY" if within noise.
Scope: %TEMP% fixtures only (never skills/, never work/) + sprint/board.md K-06 Evidence cell. No code.
Proof: 6 timings quoted (3+3 medians) + `python -m pytest tests/ -q` green (expect 32 passed) + `node sprint/check.mjs` PASS.
Stop: S/M 30 min. End with the RESULT line.
Record: K-06-measure [SELFDEV-1001] | audit before/after medians, pytest 32 passed
Board: sprint/board.md K-06 Evidence; DONE flip only if Y<X honestly, needs lead commit.
