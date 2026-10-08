---
role: builder
title: build sd-replace skill from scouted slice (BK-1007-11)
chain: start
---
Goal: serve BK-1007-11 (R1 plus R4). Build the sd-replace skill. Read the BK-1007-11 board row first for the source URL plus commit SHA plus licence (MIT read live 2026-10-08) plus trials sheet evals/sd-replace_trials.jsonl (12 tasks sd-a01 to sd-a08 plus sd-r01 to sd-r04, do not rewrite) plus failure class (find-plus-replace preview, distinct from BK-1007-1 ripgrep precision); follow the row exactly. Judge 338 PASS reviewed it (no repeat, no overlap). Follows BK-1007-10 (delta-diff 64559b5) file for file.

Scope: work/sd-replace/src/ holds 2 files (git-ignored, never committed; verify sha256 README 9908fcf5 plus input d050f790 against the row, do not re-download if they match) plus skills/sd-replace/ (SKILL plus chapters plus glossary plus patterns plus cheatsheet, 12 rules, at most 2000 tokens, ASCII, no scaffold) plus tests/test_sd_replace.py plus FLEET wire (book2skill/gates.py plus tools/install_fleet_skills.py plus 10-row evals/sd-replace_qa.jsonl so live_proof ends proven, lesson of DR-1007-12) plus `sprint/queue/done/339-book-sdreplace.md`. Own paths only, never commit.

Proof: `python tools/skill_trial.py grade --skill sd-replace` 12 runs with_rate 0.8 or more lift 0.3 or more RESULT PASS; `python tests/live_proof.py sd-replace` ends proven; lint or distill check exit 0; red replay one bad case fails before passes now; `node sprint/check.mjs` PASS. Write the done record with the RESULT plus proof lines before replying (no record, no review).

Stop: M 60 min. Claim: append `BK-1007-11 | 339-book-sdreplace | <UTC> | skills/sd-replace/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. End with the RESULT line.

End your reply with one line: `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what changed, or the blocker> | proof: <command result, file or URL>`.
