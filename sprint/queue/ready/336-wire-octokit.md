---
role: builder
title: wire octokit-request into FLEET (O-023)
chain: start
---
Goal: serve O-023 (R1). skills/octokit-request landed in BK-1007-3 DONE 2a39744 before the FLEET-wire lesson, so `python tests/live_proof.py octokit-request` ends unknown skill (center metrics judge FAIL head, import 02:33Z). Wire it: FLEET entry plus installer name plus QA so the proof ends proven. Same shape as the gron-json wire in 171ba25.

Scope: book2skill/gates.py (one FLEET line, re-read first) plus tools/install_fleet_skills.py (one name) plus new evals/octokit-request_qa.jsonl (10 rows, must-words from the skill text, mirroring evals/gron-json_qa.jsonl shape) plus `sprint/queue/done/336-wire-octokit.md`. Read the BK-1007-3 row in sprint/board-archive.md for source plus licence before writing QA. No SKILL content change, no new pairs. Own paths only, never commit.

Proof: `python tests/live_proof.py octokit-request` ends proven; `python tools/install_fleet_skills.py --to C:/Users/me/.config/opencode/skills --check octokit-request` exit 0; `node sprint/check.mjs` PASS. Write the done record with the RESULT plus proof lines before replying (no record, no review).

Stop: M 20 min. Claim: append `O-023 | 336-wire-octokit | <UTC> | book2skill/gates.py` to sprint/queue/claims.txt first, only if no claim on the row or path in the last 2 h. End with the RESULT line.

End your reply with one line: `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what changed, or the blocker> | proof: <command result, file or URL>`.
