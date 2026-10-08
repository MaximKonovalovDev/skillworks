---
role: builder
title: vivid colors skill construction run
chain: start
---
Goal: serve BK-1007-15 (R1 plus R4). Build the vivid-colors skill. Read the BK-1007-15 board row first for the source URL (sharkdp/vivid) plus commit SHA plus licence (Apache-2.0 read live 2026-10-08) plus trials sheet evals/vivid-colors_trials.jsonl (12 tasks, do not rewrite) plus failure class (color-theme: LS_COLORS theming, complements BK-1007-14 lsd plus BK-1007-4 fd); follow the row exactly. Fresh judge 362 PASS reviewed it (no repeat). Follows BK-1007-14 (lsd-ls df932f5) file for file.

Scope: work/vivid-colors/src/ holds 2 files (README 5485 sha f571b5a8, molokai 1646 sha a0dd172d; git-ignored, never committed; verify, do not re-download if they match) plus skills/vivid-colors/ (SKILL plus chapters plus glossary plus patterns plus cheatsheet, 12 rules, at most 2000 tokens, ASCII, no scaffold) plus tests/test_vivid_colors.py plus FLEET wire (book2skill/gates.py plus tools/install_fleet_skills.py plus 10-row evals/vivid-colors_qa.jsonl so live_proof ends proven, lesson of DR-1007-12) plus `sprint/queue/done/363-book-vivid.md`. Own paths only, never commit.

Proof: `python tools/skill_trial.py grade --skill vivid-colors` 12 runs with_rate 0.8 or more lift 0.3 or more RESULT PASS; `python tests/live_proof.py vivid-colors` ends proven; lint or distill check exit 0; red replay one bad case fails before passes now; `node sprint/check.mjs` PASS. Write the done record with the RESULT plus proof lines before replying (no record, no review).

Stop: M 60 min. Claim: append `BK-1007-15 | 363-book-vivid | <UTC> | skills/vivid-colors/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. End with the RESULT line.

End your reply with one line: `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what changed, or the blocker> | proof: <command result, file or URL>`.
