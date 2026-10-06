---
role: builder
title: repair cure smith (a fleet failure to a proven skill) #1
chain: repair
of: builder-cure-r1
writer: builder
attempt: 2
origin_title: cure smith (a fleet failure to a proven skill) #1
---
The judge failed builder-cure-r1. Its verdict, cut:
<task id="ses_ef1cbc12effeLKkoqBxYNw3iG9" state="completed"> <task_result> VERDICT: FAIL Changed: new `evals/red_baseline_registry.jsonl` 2 lines (001 red pipe-run 10 / 002 green 0) + `sprint/steals.md:26-27` RED-registry ideas-only line + `team/p3.md:25` run line; `tools/red_baseline_registry.py`+test already in HEAD (c539a0d), not in diff. Reran: `python tools/red_baseline_registry.py query` → `met: pipe-run 10->0 runs 001->002` exit 0 PASS; `pytest test_red_baseline_registry.py` 7 passed; `arsenal.mjs --check` RESULT PASS 13/0/0; `node sprint/check.mjs` RESULT PASS 20/0/0. Before→after: query open exit 1 → met exit 0 claimed; `round-line --check` now proven19/trials14/installed20/loads30/tools13, no before number so move unproven. Fail: scope drift — diff touches ~20 tracked files (claims.txt emptied, 6 ready/ deleted, halt deleted, board/handoff/knobs churn) vs 5 scoped paths; tool gate needs steals `landed <sha>`, has `landed uncommitted`. Fail: DR-1005-7 still READY, P2P needs pytest green — full `pytest` 2 failed/564 passed exit 1 (fleet_skills bevy + seat_guard untracked-files); export guard clean, no secret seen. Revert: `git checkout -- sprint/steals.md team/p3.md sprint/board.md sprint/queue/claims.txt sprint/handoff.md` + `Remove-Item evals/red_baseline_registry.jsonl` (plus bevy untracked if unowned). </task_result> </task>

Goal: fix exactly what the verdict names. Scope: the files of the original packet (C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-r1-review.md). Proof: the original proof plus the verdict's failing check. Stop: M 30 min; one repair only. End with the RESULT line.

Keeper facts: run builder-cure-r1-review (@judge), review cure smith (a fleet failure to a proven skill) #1.
VERDICT: FAIL
Changed: new `evals/red_baseline_registry.jsonl` 2 lines (001 red pipe-run 10 / 002 green 0) + `sprint/steals.md:26-27` RED-registry ideas-only line + `team/p3.md:25` run line; `tools/red_baseline_registry.py`+test already in HEAD (c539a0d), not in diff.
