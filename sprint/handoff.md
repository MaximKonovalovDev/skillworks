# skillworks handoff - round 368 (token d5a1)

Round: 368 (lock d5a1 held since 11:24Z)
Written: 2026-10-09T11:24Z
Token: d5a1
Knobs: width 1, foreground batches (keeper batch stale, lead decides per owner GO).

## Heading
- Second crash, same rule: interrupted cure left claim DR-1006-2 10:16Z but no skill diff. Replanned as pinned light retry 373 (no full suite, hard 25 min box).

## Batch sent (ONE message, 1 Task call, prompt exactly packet:<name>)
- builder 373-cure-taskscope-retry.

## Rows
- DR-1006-2 stays READY (crash claim reused, no double-claim).
- DONE this wave: DR-1006-6 8be1132, DR-1006-5 e59af71, DR-1006-4 1c00f0e, DR-1006-3 fe43b04.
- AD-1006-1 plus AD-1006-2 READY (clocks to 2026-10-11).

## Blockers
- Two interrupted runs this session (installer, cure). Pattern: long runs die; fix is smaller boxes plus no full suite in builder packets (judge runs it).

## Checks
- node sprint/check.mjs PASS 20/0/0 (standing).
- Commit e5a31a1 (1 file, clean). Tree nearly clean except keeper runtime.

## Next
- Collect retry, review, land. Then planner inbox-rowing wave.

RESULT: PARTIAL - crash replanned as light retry 373, result pending | proof: RESULT PASS: 20 pass, 0 warn, 0 fail
