---
role: judge
title: review K-09 rarity-weighted rank (freud 0.50 to 0.833)
---

Goal: Judge builder K-09 (index.py search() tf.idf log((N+1)/(df+1))+1 per query word, tokenization/counting/signature unchanged, eval.py untouched + tests/test_rarity_rank.py discriminator + freud 6/12=0.50 REFUSED to 10/12=0.833 re-logged in evals/seeds_qa.jsonl, gate 0.6 untouched, no QA edits) for commit. Serves R2. DECIDE: tracked skills/freud-dream-psychology/eval_report.json still pins 0.5 and test_mcp_rank pins the 0.5 expectation — PASS with a follow-up row (refresh report + pinned expectation), or FAIL requiring it now? Builder left it deliberately (test-expectation edits out of scope).
Scope: book2skill/index.py (search weighting only) + tests/test_rarity_rank.py (new only) + evals/seeds_qa.jsonl (re-logged rate only).
Proof: rerun `python -m pytest tests/ -q` yourself (expect 32 passed); rare-term chunk outranks generic repeater on fixture; gate still refuses sub-0.6 (tracked freud report exit 1); progit 12/12=1.0 intact; before/after 0.46s to 0.51s sane.
Stop: read-only, at most 15 lines, VERDICT PASS/FAIL/BLOCKED with what changed, checks before/after, revert + the report-refresh verdict.
Record: K-09 [BLOCKED-DEEPDIVE-1001] | rarity rank, freud 0.833, pytest 32 passed
Result: K-09 RESULT DONE 2026-10-03
