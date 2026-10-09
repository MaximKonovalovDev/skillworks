# skillworks handoff - round 356 (token d5a1)

Round: 356 (lock d5a1 held since 22:05Z)
Written: 2026-10-09T00:35Z
Token: d5a1
Knobs: width 1, foreground batches (keeper batch stale, lead decides per owner GO BIG).

## Heading
- Judge FAIL on allowlist v1.2.0: skill shape holds (grade 22 runs 1.0/0.0 lift 1.0, live proven, lint ok) but suite count grew, halving unmet (UP 520 to 933), 16 files drift outside owned set. One builder repair next.

## Batch sent (ONE message, 1 Task call, prompt exactly packet:<name>)
- judge 366-cure-allowlist-v12-review.

## Rows
- DR-1006-6 stays READY (first FAIL; chain gives one repair, second FAIL comes to lead).
- DR-1006-3 spawn-guard bump waits behind this repair.

## Blockers
- 48 h halving cannot pass same-day: needs adoption plus clock. Repair must say so, not fake it.
- Tree drift (16 files incl gates.py+145, make, mcp_server) vs pre-existing dirty tree: repair separates bump-owned from others' drift.

## Checks
- node sprint/check.mjs PASS 20/0/0 (judge reran, same).
- Commit a008947 (2 files, clean).

## Next
- builder 367-cure-allowlist-v12-repair (M 25 min), then re-review. PASS lands v1.2.0; second FAIL comes to lead for replan or OWNER row.

RESULT: PARTIAL - FAIL reviewed, one repair queued | proof: RESULT PASS: 20 pass, 0 warn, 0 fail
