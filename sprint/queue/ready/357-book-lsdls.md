---
role: builder
title: fresh assembly of lsd-ls skill slice
chain: start
---
Goal: serve BK-1007-14 (R1 plus R4). Build the lsd-ls skill. Read the BK-1007-14 board row first for the source URL plus commit SHA plus licence (Apache-2.0 read live 2026-10-08) plus trials sheet evals/lsd-ls_trials.jsonl (12 tasks, do not rewrite) plus failure class (directory-listing: classify/tree/git/long/sort, complements BK-1007-4 fd plus BK-1007-9 bat); follow the row exactly. Fresh judge 356 PASS reviewed it (no repeat). Follows BK-1007-13 (hyperfine-bench 4aa6aca) file for file.

Scope: work/lsd-ls/src/ holds 2 files (git-ignored, never committed; verify sha256 71014929 plus c140e0c4 against the row, do not re-download if they match) plus skills/lsd-ls/ (SKILL plus chapters plus glossary plus patterns plus cheatsheet, 12 rules, at most 2000 tokens, ASCII, no scaffold) plus tests/test_lsd_ls.py plus FLEET wire (book2skill/gates.py plus tools/install_fleet_skills.py plus 10-row evals/lsd-ls_qa.jsonl so live_proof ends proven, lesson of DR-1007-12) plus `sprint/queue/done/357-book-lsdls.md`. Own paths only, never commit.

Proof: `python tools/skill_trial.py grade --skill lsd-ls` 12 runs with_rate 0.8 or more lift 0.3 or more RESULT PASS; `python tests/live_proof.py lsd-ls` ends proven; lint or distill check exit 0; red replay one bad case fails before passes now; `node sprint/check.mjs` PASS. Write the done record with the RESULT plus proof lines before replying (no record, no review).

Stop: M 60 min. Claim: append `BK-1007-14 | 357-book-lsdls | <UTC> | skills/lsd-ls/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. End with the RESULT line.

End your reply with one line: `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what changed, or the blocker> | proof: <command result, file or URL>`.
