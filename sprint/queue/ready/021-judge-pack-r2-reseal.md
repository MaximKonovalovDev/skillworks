---
role: judge
title: review pack-r2 licence reseal plus 10 live-proof reseals
chain: review
of: builder-pack-r2
writer: builder
attempt: 1
origin_title: pack maker licence reseal plus reseals
---

Review builder-pack-r2 (claim pack.token 2026-10-05T09:33Z), built by builder. Its record: claim line in sprint/queue/claims.txt for packs/fleet-vol-1 plus THIRD_PARTY_NOTICES.md plus team/p5.md. The builder-pack-r1 judge PASS is stale (listing plus live-proof bytes moved since). Rerun proof on current bytes, read the diff, check the pack done-when (RESULT PASS). You never edit.

Goal: judge the current on-disk pack state: licence re-read dates plus 10 resealed live proofs.

Scope: packs/fleet-vol-1/listing.md, THIRD_PARTY_NOTICES.md (re-read 2026-10-05 lines), team/p5.md (2026-10-05T09:33Z plus 2026-10-05T10:03Z lines), skills/bevy-rust-ecs plus cron-skip-clean plus edit-reread plus engine-builder plus git-one-branch plus inbox-file-reader plus pipe-run plus pwsh-for-bash-writers plus real-browser-automation plus repo-read-first references/live-proof.json (resealed 2026-10-05T09:52-09:53Z).

Proof: python tools/pack_check.py packs/fleet-vol-1 ends RESULT PASS 13 checks 0 warnings; licence line of every source matches references/sources.md; no NonCommercial source priced; SKILL_LIVE=1 re-prove of the 2 Proof-date skills named in listing (real-browser-automation 11 passed, bevy-rust-ecs 42 passed); python -m pytest tests/ -q and node sprint/check.mjs equal or better than before (434 passed 116 skipped, 20/0/0); Get-ChildItem skills -Recurse -Directory -Filter export empty and no path over 240 chars; no other repo path/text/number, no secret; ONE REAL THING: pack gate FAIL 4 (handoff r175) to PASS 13 on disk, or FAIL paperwork.

Stop: M 30 min; judge only, no edits; never commit. End with VERDICT: PASS|FAIL|BLOCKED plus what changed, checks before/after with numbers and the one real thing, and how to revert, in at most 15 lines.
