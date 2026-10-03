---
role: builder
title: repair builder-rows-r1 (K-04 progit QA source-derived)
---

Goal: Fix exactly what the judge FAIL names: replace progit stub QA (single-word must like nearly/pickle, tests nothing) with source-derived QA; keep freud hand-authored set; do NOT touch sprint/halt (center turned it OFF in 2717c6f to start the loop; restoring it stops the loop).
Scope: evals/progit-branching_qa.jsonl, evals/seeds_qa.jsonl (re-log), skills/progit-branching/ (only if the skill must change to answer the QA; never edit tests to pass).
Proof: K-04 done-when (2 skills in skills/<name>/ with eval pass-rate logged, `python -m pytest tests/ -q` green) plus the verdict's failing check (every progit QA q names a real branching concept, must terms multi-word where the concept needs it, no nearly/pickle-class stubs; show before/after QA sample + rates).
Stop: M 30 min; one repair only. End with the RESULT line.
Record: builder-rows-r1 | evals/progit-branching_qa.jsonl stubs -> source-derived + re-logged rates
Verdict: VERDICT FAIL builder-rows-r1 K-04 (placeholder progit QA; pytest 7 passed rerun) - halt-restore demand overruled by lead (2717c6f ON turned halt off; restoring stops the loop).
