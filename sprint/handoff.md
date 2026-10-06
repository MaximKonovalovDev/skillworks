# skillworks handoff - round 235 (token 1803)

Round: 235 (read-offset v1.2.0 landed, allowlist repaired, edit-verify bumped, retro done)
Written: 2026-10-06T18:20Z
Token: 1803 (takeover 2026-10-06T15:24Z, replaced stale lead#a7e2 left by closed app)
Knobs: width 5, foreground, heavy_max 3, paid_mode 0 (file of 2026-10-06T00:14Z, unchanged).

## Heading
- R1 book-to-skill: read-offset-guard v1.2.0 landed (10 new pairs 12->22, grade 1.0/0.0). No class halved yet (needs adoption + 48 h).

## Results collected
- builder-cure-r8-repair (builder): DONE trials 17 tasks +5 no narrowing, red/green recorded, grade 17 runs 1.0/0.0 PASS. Review queued (fresh one-off).
- builder-cure-r9-review (judge): VERDICT PASS stacked r7+r9, moved not paperwork. Committed 32c8d66 (7 files).
- builder-pack-r5-review (judge): VERDICT FAIL paperwork (dist ignored, only p5 line tracked, nothing moved). Closed: gate PASS stands, nothing tracked to land by design.
- researcher-toolsmith-r9: NOOP all green (arsenal 13/0/0).
- builder-cure-r10 (builder): DONE edit-verify v0.2.0 bump (5 new pairs 12->17, all green). Review queued (fresh one-off).

## Rows
- DR-1006-5 READY v1.2.0 in 32c8d66 (class-halve pending adoption + 48 h). DR-1006-6 READY (repair DONE, review next).
- DR-1006-4 READY (v0.2.0 built, review next). DR-1006-7 READY (cure next). BK-1006-3 DONE 1e04111.
- K-54 OWNER, K-03 K-06 PARKED, BK-1004-1 BLOCKED. S50 open 1 of 5.

## Checks
- node sprint/check.mjs RESULT PASS 20 pass 0 warn 0 fail (lead reran).
- Lead reran: live_proof read-offset-guard proven 6 passed. Judges report 605-606 green + seat-guard untracked (concurrent, out of scope).

## Held, not committed
- Allowlist v1.1.0+repair files + red record, edit-verify v0.2.0 files, websearch red test, team/p3.md lines, timestamp noise (land after reviews).

## Next
- Keeper batch 17:47Z all stale (037/r6/r7 judged, r8-repair DONE, toolsmith NOOP). Lead replaces with fresh: r8-repair review, r10 review, toolsmith, cure, doctor.
- Then: land allowlist + edit-verify on PASS, cure DR-1006-7, adoption scan.

## Retro (round 235, due)
- Metrics 18:06Z: judge PASS 22/43 FAIL 21. Last FAILs: allowlist done-when + paperwork x2. Top: 8x keeper readiness hold (new), 5x SKILL_LIVE=1 bash-in-pwsh (down from 8), 4x read-missing target-class.json (new).
- Worst repeated: judges FAIL green work that moves no tracked number (paperwork: r6 timestamps, pack dist, r5 25->25) — 3 this round; plus builders hitting missing target-class.json on bump rows (4x).
- PROPOSAL: sprint/queue/standing/builder-cure.md | verify skills/<name>/references/target-class.json exists before claiming the row (doctor creates it with the red test; bump rows on skills lacking it hit read-missing) | read-missing target-class.json 4x in 24 h now
- Coach: no coach change (part scores flat, P1 8/8 P3 33+ skills). Next retro due 240.
