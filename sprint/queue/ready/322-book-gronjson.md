---
role: builder
title: build gron-json skill from scouted slice (BK-1007-8)
chain: start
---
Goal: serve BK-1007-8 (R1 plus R4). Build the gron-json skill (gron assignments plus ungron round-trip for the structured-data query class, complements BK-1007-5 yq-jq). Scout laid the slice: work/gron-json/src/ 2 files (sha256 8015dc plus c9c98b, git-ignored, never committed) plus evals/gron-json_trials.jsonl (12 tasks gr-a01 to gr-a08 plus gr-r01 to gr-r04, RESULT PASS). Follows BK-1007-5 (yq-jq 39999f4) file for file. Judge 321 PASS reviewed the row: licence MIT read live 2026-10-07, no repeat, no secret.

Scope: skills/gron-json/ (SKILL plus chapters plus glossary plus patterns plus cheatsheet, 12 rules, at most 2000 tokens, ASCII, no scaffold; adopt the judge's grade side-effect dir if present, else create it) plus tests/test_gron_json.py plus FLEET wire (book2skill/gates.py plus tools/install_fleet_skills.py plus 10-row evals/gron-json_qa.jsonl so live_proof ends proven, lesson of DR-1007-12) plus `sprint/queue/done/322-book-gronjson.md`. Do not rewrite the trials sheet. Own paths only, never commit. Re-read the sheet plus one BK-1007-5 skill file for shape before writing.

Proof: `python tools/skill_trial.py grade --skill gron-json` 12 runs with_rate 0.8 or more lift 0.3 or more RESULT PASS; `python tests/live_proof.py gron-json` ends proven; lint or distill check exit 0; red replay one bad case fails before passes now; `node sprint/check.mjs` PASS. Write the done record with the RESULT plus proof lines before replying (no record, no review).

Stop: M 60 min. Claim: append `BK-1007-8 | 322-book-gronjson | <UTC> | skills/gron-json/` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. End with the RESULT line.

End your reply with one line: `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what changed, or the blocker> | proof: <command result, file or URL>`.
