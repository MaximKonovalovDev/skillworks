# skillworks handoff - round 55 (token f3a9)

Round: 55
Written: 2026-10-03T14:12Z
Token: f3a9 (takeover 2026-10-03T13:23Z from b7e2; refreshed 13:49Z)
Knobs: width 2, dispatch foreground, heavy_max 3, helper_max 90m, bg_width 0, cards_per_reader 5 (no change, no proposal).

## Heading
- R4 moves: K-28 DONE (freud header/footer stripped). 015 pilot defect fixed, awaits judges.

## Done
- Judge-018 PASS on K-28 (reimpl MIT idea, no paste; opt-out verified 1241682 stripped:false). Committed ece6df6 (extract.py + 1 test). Board K-28 READY->DONE.
- Builder-015 DONE (chain: needs judge): server.py --skills-dir flag + $SKILLWORKS_SKILLS_DIR/$SKILLS_DIR + unknown-skill isError envelope naming served dir; K-29 schema intact; tests/test_mcp_skills_dir.py + 1 README line. pytest 19 passed. NOT committed (mixed with unjudged K-29 in server.py).

## Checks
- python -m pytest tests/ -q: 19 passed in 1.86s.
- node sprint/check.mjs: 20 pass, 1 warn, 0 fail.

## Blockers
- server.py now stacks K-29 + 015 (both unjudged): needs judge-K-29 then judge-015 in order, or one combined review. Still await judges: K-23, K-08 (+016 fix open).
- Builder + vision seats held. Follow-up: THIRD_PARTY_NOTICES.md kiasar/gutenberg_cleaner line (from 018).

## Next
- Keeper: please name judge-K-29 + judge-015 (server.py stack) next.
