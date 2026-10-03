---
role: judge
title: review K-08 shop slice (listing + Vol 0 + demo GIF placeholder)
---

Goal: Judge builder K-08 (skills/progit-branching/listing.md + vol0-sample.md + demo/demo.gif 43B placeholder) for commit. Serves R6. Listing is PREP-ONLY by design (not shipped) — judge honesty, not sales.
Scope: skills/progit-branching/listing.md + vol0-sample.md + demo/demo.gif (3 new files only, no code).
Proof: rerun `node sprint/check.mjs` yourself (expect 20/1/0) + `python -m pytest tests/ -q` (expect 19 passed); verify listing states PREP-ONLY + sales 0 + placeholder disclosed + source license CC BY-NC-SA 3.0 named; verify vol0 sample derives from the cheatsheet; verify demo.gif is valid GIF89a.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-08 [WEAKEST-R6-1001] | listing + Vol 0 + GIF placeholder, honest, check 20/1/0
Result: K-08 RESULT DONE 2026-10-03
