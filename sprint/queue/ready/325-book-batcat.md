---
role: builder
title: build bat-cat skill from scouted slice (BK-1007-9)
chain: start
---
Goal: serve BK-1007-9 (R1 plus R4). Build the bat-cat skill. Read the BK-1007-9 board row first for the source URL plus commit SHA plus licence (Apache-2.0 read live 2026-10-07) plus trials sheet evals/bat-cat_trials.jsonl plus failure class; follow the row exactly. Judge 324 PASS reviewed it (no repeat, licence clean). Follows BK-1007-8 (gron-json 171ba25) file for file.

Scope: work/bat-cat/src/ already holds 2 files (git-ignored, never committed; verify sha256 against the row, do not re-download if they match) plus evals/bat-cat_trials.jsonl (12 tasks, do not rewrite) plus skills/bat-cat/ (SKILL plus chapters plus glossary plus patterns plus cheatsheet, 12 rules, at most 2000 tokens, ASCII, no scaffold) plus tests/test_bat_cat.py plus FLEET wire (book2skill/gates.py plus tools/install_fleet_skills.py plus 10-row evals/bat-cat_qa.jsonl so live_proof ends proven, lesson of DR-1007-12) plus `sprint/queue/done/325-book-batcat.md`. Own paths only, never commit.

Proof: `python tools/skill_trial.py grade --skill bat-cat` 12 runs with_rate 0.8 or more lift 0.3 or more RESULT PASS; `python tests/live_proof.py bat-cat` ends proven; lint or distill check exit 0; red replay one bad case fails before passes now; `node sprint/check.mjs` PASS. Write the done record with the RESULT plus proof lines before replying (no record, no review).

Stop: M 60 min. Claim: append `BK-1007-9 | 325-book-batcat | <UTC> | skills/bat-cat/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. End with the RESULT line.

End your reply with one line: `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what changed, or the blocker> | proof: <command result, file or URL>`.
