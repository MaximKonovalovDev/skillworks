---
role: builder
title: build hyperfine-bench skill from scouted slice (BK-1007-13)
chain: start
---
Goal: serve BK-1007-13 (R1 plus R4). Build the hyperfine-bench skill. Read the BK-1007-13 board row first for the source URL plus commit SHA plus licence (Apache-2.0 read live 2026-10-08) plus trials sheet evals/hyperfine-bench_trials.jsonl (12 tasks hb-a01 to hb-a08 plus hb-r01 to hb-r04, do not rewrite) plus failure class (benchmark-timing: warmup, param-scan, outliers); follow the row exactly. Judge 350 PASS reviewed it (no repeat). Follows BK-1007-12 (hexyl-hex 06ed811) file for file.

Scope: work/hyperfine-bench/src/ holds 2 files (git-ignored, never committed; verify sha256 03e31b plus c1fe01 against the row, do not re-download if they match) plus skills/hyperfine-bench/ (SKILL plus chapters plus glossary plus patterns plus cheatsheet, 12 rules, at most 2000 tokens, ASCII, no scaffold) plus tests/test_hyperfine_bench.py plus FLEET wire (book2skill/gates.py plus tools/install_fleet_skills.py plus 10-row evals/hyperfine-bench_qa.jsonl so live_proof ends proven, lesson of DR-1007-12) plus `sprint/queue/done/351-book-hyperfine.md`. Own paths only, never commit.

Proof: `python tools/skill_trial.py grade --skill hyperfine-bench` 12 runs with_rate 0.8 or more lift 0.3 or more RESULT PASS; `python tests/live_proof.py hyperfine-bench` ends proven; lint or distill check exit 0; red replay one bad case fails before passes now; `node sprint/check.mjs` PASS. Write the done record with the RESULT plus proof lines before replying (no record, no review).

Stop: M 60 min. Claim: append `BK-1007-13 | 351-book-hyperfine | <UTC> | skills/hyperfine-bench/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. End with the RESULT line.

End your reply with one line: `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what changed, or the blocker> | proof: <command result, file or URL>`.
