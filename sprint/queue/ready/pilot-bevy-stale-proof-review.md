---
role: judge
title: review bevy stale-proof reseal
chain: review
of: pilot-bevy-stale-proof
writer: builder
attempt: 1
origin_title: reseal bevy-rust-ecs stale live proof (Vol1 member failing gates)
---
Review pilot-bevy-stale-proof, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\pilot-bevy-stale-proof.md (if missing, judge the tree and say so). Rerun the proofs yourself, read the diff. You never edit. Scope: skills/bevy-rust-ecs/ plus its live proof only; concurrent dirt out of scope. Distinct from DR-1005-9 DONE (viewer aborts); this is proof staleness.

Rerun and paste each result line:
1. `python -m pytest tests/ -q -k "bevy"` green (the 3 named FAILs gone: qa-musts, eval gate, live-proof match).
2. `python tests/live_proof.py bevy-rust-ecs` ends proven with a fresh timestamp; eval rate at gate.

Always: (a) full pytest plus check equal or better than before (pre-existing out-of-scope fails named, not charged); (b) privacy: no other repo's path, text or number, no secret; (c) only owned files changed; no weakened gate, no edited QA to make a rate pass (musts appearing by skill fix is fine, by QA edit is FAIL); (d) ONE REAL THING: the 3 bevy FAILs flip on this diff.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Built result, cut:
<task_result> RESULT: DONE - bevy-rust-ecs passes its own gates again (musts + eval + fresh live proof) | proof: python -m pytest tests/ -q -k "bevy" -> 50 passed, 3 skipped in 12.03s </task_result>

Keeper facts: run pilot-bevy-stale-proof (seat builder, @builder), reseal bevy-rust-ecs stale live proof.
