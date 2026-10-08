---
role: builder
title: build hexyl-hex skill from scouted slice (BK-1007-12)
chain: start
---
Goal: serve BK-1007-12 (R1 plus R4). Build the hexyl-hex skill. Read the BK-1007-12 board row first for the source URL (sharkdp/hexyl) plus commit SHA plus licence (Apache-2.0 plus MIT read live 2026-10-08) plus trials sheet evals/hexyl-hex_trials.jsonl (12 tasks hx-a01 to hx-a08 plus hx-r01 to hx-r04, do not rewrite) plus failure class (binary-read, complements BK-1007-9 plus BK-1007-1); follow the row exactly. Judge 344 PASS reviewed it (no repeat). Follows BK-1007-11 (sd-replace 0194669) file for file.

Scope: work/hexyl-hex/src/ holds 2 files (git-ignored, never committed; verify sha256 against the row, do not re-download if they match) plus skills/hexyl-hex/ (SKILL plus chapters plus glossary plus patterns plus cheatsheet, 12 rules, at most 2000 tokens, ASCII, no scaffold) plus tests/test_hexyl_hex.py plus FLEET wire (book2skill/gates.py plus tools/install_fleet_skills.py plus 10-row evals/hexyl-hex_qa.jsonl so live_proof ends proven, lesson of DR-1007-12) plus `sprint/queue/done/345-book-hexylhex.md`. Own paths only, never commit.

Proof: `python tools/skill_trial.py grade --skill hexyl-hex` 12 runs with_rate 0.8 or more lift 0.3 or more RESULT PASS; `python tests/live_proof.py hexyl-hex` ends proven; lint or distill check exit 0; red replay one bad case fails before passes now; `node sprint/check.mjs` PASS. Write the done record with the RESULT plus proof lines before replying (no record, no review).

Stop: M 60 min. Claim: append `BK-1007-12 | 345-book-hexylhex | <UTC> | skills/hexyl-hex/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. End with the RESULT line.

End your reply with one line: `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what changed, or the blocker> | proof: <command result, file or URL>`.
