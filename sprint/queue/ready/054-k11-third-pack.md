---
role: builder
title: K-11 third domain pack (1-pack-week cadence proof)
chain: start
---

Goal: K-11 DONE (R4): third domain pack proving cadence — second psychology PD book (James, Gutenberg, public domain ONLY) OR second programming open-license book into work/ (gitignored, never commit the book), then skills/<name>/ built with eval rate logged. Mirror K-04 pattern (extract, split, index, build, eval QA, gate respected).
Scope: work/<new>/ (new, gitignored) + skills/<new>/ (new) + evals/<new>_qa.jsonl (new, source-derived QA) + 1 eval test entry if the suite pattern requires it. No other skills touched. Gutenberg download allowed (PD/open-license only — verify license header before building).
Proof: 3rd skill in skills/<name>/ with eval rate logged + `python -m pytest tests/ -q` green + book license verified PD/open in Evidence.
Stop: L 60 min (download + full pipeline; PARTIAL with download+evals logged is acceptable if build needs a follow-up). End with the RESULT line.
Record: K-11 [G3-EDGE-1001] | 3rd pack + eval rate, pytest green
Board: sprint/board.md K-11 READY -> DONE needs judge PASS + commit by lead.
