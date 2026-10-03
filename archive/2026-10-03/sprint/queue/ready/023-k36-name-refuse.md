---
role: builder
title: K-36 build refuses name/dir mismatch (016 pilot defect)
chain: start
---

Goal: K-36 DONE (R1): book2skill/build.py (+cli wiring) errors when --name != skill dir basename or breaks a-z0-9-, quoting the rule. Closes pilot 016 defect (verbatim exit-0 silent mismatch proven r3+r4).
Scope: book2skill/build.py + book2skill/cli.py (wiring only) + ONE mismatch test (tests/test_pipeline.py or new tests/test_build_name.py). No README change (rule already documented), no other skills, no server.py/extract.py.
Proof: mismatched pair (name != dir) exit !=0 with rule quoted + matching pair still builds + `python -m pytest tests/ -q` green (expect 20 passed: 19 + 1 new).
Stop: S/M 30 min, end-to-end (fix + test + proof). End with the RESULT line.
Record: K-36 [016] | name/dir refuse + test, pytest 20 passed
Board: sprint/board.md K-36 READY -> DONE needs judge PASS + commit by lead.
