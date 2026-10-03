# skillworks handoff - round 64 (token f3a9)

Round: 64
Written: 2026-10-03T14:45Z
Token: f3a9 (takeover 2026-10-03T13:23Z from b7e2; refreshed 13:49Z)
Knobs: width 2, dispatch foreground, heavy_max 3, helper_max 90m, bg_width 0, cards_per_reader 5 (no change, no proposal).

## Heading
- K-36 DONE (016 defect closed, 20 tests green). One-off packets bypass seat holds.

## Done
- Builder-023 one-off K-36 DONE: NAME_RULE + UsageError exit 2, layout test fixed, new mismatch test. pytest 20 passed.
- Judge-024 PASS (direct build() ValueError + charset exit 2 verified). Committed 5ea7796 (3 files). Board K-36 READY->DONE.
- Wrote packets 023 (used) + 024 (used) in ready/.

## Checks
- python -m pytest tests/ -q: 20 passed.
- node sprint/check.mjs: 20 pass, 0 warn, 0 fail.

## Blockers
- K-27 OWNER + K-39 BLOCKED. Builder/vision seat holds (one-offs still work).
- THIRD_PARTY_NOTICES.md kiasar line open.

## Next
- Keeper: one-off builder packets (K-24/K-26/K-37/K-38) or hold status.
