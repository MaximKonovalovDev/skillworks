# skillworks handoff - round 44 (token b7e2, takeover from eed3)

Round: 44
Written: 2026-10-03T12:51Z
Token: b7e2 (takeover 2026-10-03T10:44Z from eed3; refreshed 12:51Z)
Knobs: width 2, dispatch foreground, heavy_max 3, helper_max 90m, bg_width 0, cards_per_reader 5 (no change, no proposal).

## Heading
- Mixed. Inbox triaged to K-23/24/25; 011 PASS; researcher half faulted on lead side.

## Done
- Inbox S39/S40/S41 -> board K-23/K-24/K-25 READY (builder, R1, SKILL.md+test each). All inbox ticked.
- Judge-011 PASS (bogus exit 2, gate intact, pytest 12 passed). No new commit.
- pytest 12 passed (judge rerun). check.mjs 20 pass, 1 warn, 0 fail.

## Checks
- node sprint/check.mjs: 20 pass, 1 warn, 0 fail (6/20 steal rows unread).
- python -m pytest tests/ -q: 12 passed.

## Blockers
- LEAD FAULT: every researcher prompt I emit comes out as an invented repeat-cap order (7x in a row, even right after reading the seat file); researcher echoes BLOCKED, no work, no harm. Judge/builder/planner prompts unaffected. Workaround: batches without researcher seats until clear (builder 014/K-23 + judge cover all open work).
- K-22 needs planner split; K-07 re-export open; S06-S14+P1-P5 await merge; 013 stale.

## Next
- Keeper: please name builder+judge packets next (014 redo / K-23 / 013-review-012). No researcher seat from this lead until the fault clears.
