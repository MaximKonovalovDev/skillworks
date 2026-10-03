---
role: builder
title: K-09 freud rarity-weighted pipeline ranking
chain: start
---

Goal: K-09 DONE (R2): rarity-weighted substring search in pipeline ranking — generic query words must not swamp rare terms over freud's 259 chunks. QA-side fixes exhausted, gate held, NO test edits (do not touch evals/* or test expectations to pass).
Scope: book2skill/index.py and/or book2skill/eval.py ranking code (weighting only) + ONE test (rare-term query outranks generic-word query on a fixture; freud pass rate re-logged). No evals/ edits, no gate threshold change (0.6 stays).
Proof: freud pass rate re-logged in evals/seeds_qa.jsonl (number reported, gate still holds if below) + `python -m pytest tests/ -q` green + before/after timing in Evidence.
Stop: M 45 min (hard row; PARTIAL with measured progress is acceptable if gate behavior verified intact). End with the RESULT line.
Record: K-09 [BLOCKED-DEEPDIVE-1001] | rarity-weighted rank, freud rate re-logged, pytest green
Board: sprint/board.md K-09 READY -> DONE needs judge PASS + commit by lead.
