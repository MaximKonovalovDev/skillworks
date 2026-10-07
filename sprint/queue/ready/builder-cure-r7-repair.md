---
role: builder
title: repair cure smith (a fleet failure to a proven skill) #7
chain: repair
of: builder-cure-r7
writer: builder
attempt: 2
origin_title: cure smith (a fleet failure to a proven skill) #7
---
The judge failed builder-cure-r7. Its verdict, cut:
<task id="ses_eea63b33cffeLipZLG2F0avbx2" state="completed"> <task_result> VERDICT: FAIL What changed: nothing by r7 — `git diff HEAD -- skills/read-offset-guard/` is empty; tree already at v1.3.0 via prior commits a91bdcd/32c8d66, not the claimed v1.0.0→v1.1.0. Claimed 5 pairs (ro-deep44/ro-queue32/ro-index542/ro-index541/ro-handoff28), shrink-limit rule, v1.1.0 bump: all already in HEAD, not this packet's diff. Packet numbers stale (claims 13 rules/636 tok/26 pairs; tree has 19 rules/851 tok/27 pairs.json entries, lint pairs 39). My rerun: `python tests/live_proof.py read-offset-guard` → proven, 6 passed (matches); `skill_lint.py check --skill skills/read-offset-guard` → RESULT PASS (19 rules, 39 locators/pairs, 851 tok); `pytest tests/test_read_offset_guard.py` → 3 passed 3 skipped (matches); export guard clean (no `skills/**/export`). ONE REAL THING: none moved by r7 — empty owned diff, so FAIL "paperwork" per rule, even though commands are green. Fleet round-line (proven 41/trials 36/installed 27) not attributable to this packet. Scope: working tree dirty with unrelated concurrent work (bash-allowlist, lead2, queue deletions), none of it r7's claimed files. Revert: no-op — nothing to revert; do not commit; claimed content already landed under a91bdcd/32c8d66. </task_result> </task>

Goal: fix exactly what the verdict names. Scope: the files of the original packet (C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-cure-r7-review.md). Proof: the original proof plus the verdict's failing check. Stop: M 30 min; one repair only. End with the RESULT line.

Keeper facts: run builder-cure-r7-review (@judge), review cure smith (a fleet failure to a proven skill) #7.
VERDICT: FAIL
