# skillworks handoff - round 71 (token f3a9)

Round: 71
Written: 2026-10-03T15:31Z
Token: f3a9 (takeover 2026-10-03T13:23Z from b7e2; refreshed 13:49Z)
Knobs: width 2, dispatch foreground, heavy_max 3, helper_max 90m, bg_width 0, cards_per_reader 5 (no change, no proposal).

## Heading
- Two more DONE: K-17 (preview) + K-18 (frontmatter). Session: 21 rows DONE, 28 tests.

## Done
- Judge-042 PASS (K-17 both tools live). Committed f932b4b. Board K-17 READY->DONE.
- Judge-043 PASS (K-18 order + NAME_RULE intact). Committed d8ceb71. Board K-18 READY->DONE.
- Wrote packets 040/041 (used) + 042/043 (used) in ready/.

## Checks
- python -m pytest tests/ -q: 28 passed.
- node sprint/check.mjs: 20 pass, 0 warn, 0 fail.

## Blockers
- K-27 OWNER + K-39/K-21/K-22 BLOCKED. Holds persist; one-offs carry the loop.
- Left READY: K-01 TOP, K-03/05/06/09/11-16/19/20.

## Next
- Keeper: one-offs for K-16/K-20/K-19 or hold status.
