---
role: judge
title: review K-37/K-38 listing shape + files block (docs only)
---

Goal: Judge builder K-37/K-38 (listing.md +status/category/tags/files block + Vol 0 filename+size+date, PREP-ONLY kept, no paid ship, no ToS paste, no fee numbers) for commit. Serves R6.
Scope: skills/progit-branching/listing.md (docs lines only).
Proof: rerun `node sprint/check.mjs` yourself (expect 20/0/0) + `python -m pytest tests/ -q` (expect 21 passed); verify status+category+tags+files present, Vol 0 line has filename+size+date, PREP-ONLY + sales 0 + CC BY-NC-SA still stated, no price/fee numbers added as fact.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert.
Record: K-37/K-38 [S19-C2/C4] | listing shape + files block, PREP-ONLY, check PASS
Result: K-37/K-38 RESULT DONE 2026-10-03
