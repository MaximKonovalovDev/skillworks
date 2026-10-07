---
role: builder
title: narrow fix write-abort installer wire plus cleanup (DR-1007-12)
chain: start
---
Goal: close the 310 FAIL gaps without touching proven skill content (grade 12 runs 1.0/0.0 lift 1.0, lint PASS, live_proof proven all stand). Second FAIL came to the lead; this narrow fix is the replan.

Scope: tools/install_fleet_skills.py (add write-abort-guard to the FLEET list, same shape as read-abort-guard; re-read the file first, small oldString) plus delete root chunk.txt plus skills/write-abort-guard scripts __pycache__ plus append the missing claim `DR-1007-12 | 317-writeabort-fix | <UTC> | tools/install_fleet_skills.py` to sprint/queue/claims.txt. Nothing else: no SKILL change, no new pairs, no QA edits. Own paths only, never commit.

Proof: `python tools/install_fleet_skills.py --to C:/Users/me/.config/opencode/skills --check write-abort-guard` exit 0; `python tests/live_proof.py write-abort-guard` ends proven; `node sprint/check.mjs` PASS. Write `sprint/queue/done/317-writeabort-fix.md` with the RESULT plus proof lines before replying (no record, no review).

Stop: M 20 min. Claim first as above, only if no claim on the row or path in the last 2 h. End with the RESULT line.

End your reply with one line: `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what changed, or the blocker> | proof: <command result, file or URL>`.
