# skillworks handoff - round 247 (token 1803)

Round: 247 (batch collected 1 DONE plus 4 PARTIAL, 3 reviews plus 1 finish queued)
Written: 2026-10-07T02:15Z
Token: 1803 (takeover 2026-10-06T15:24Z, replaced stale lead#a7e2 left by closed app)
Knobs: width 5, foreground, heavy_max 3, paid_mode 0 (file of 2026-10-06T00:14Z, unchanged).

## Heading
- R1/R2 fixes: readyfile DONE (v1.1.0, lift 1.0), ripgrep plus skiphint plus auditfold PARTIAL with F2P met, agentlint PARTIAL blocked on readyfile landing.

## Results collected
- builder-cure-readyfile: DONE DR-1007-1 v1.1.0, red 1/5 to 5/5, grade 1.0/0.0, live 6, check 20/0/0. Review queued.
- builder-book-ripgrep: PARTIAL BK-1007-1 built, grade 1.0/0.25 lift 0.75, live 11; gap is 1-line FLEET_SKILLS wiring plus credit (lead-scoped, out of builder scope). Finish queued.
- builder-fix-skiphint: PARTIAL O-006 F2P met (SKILL_LIVE warning prints, live 18 passed with =1), check PASS. Review queued.
- builder-fix-agentlint: PARTIAL O-007 both proofs resealed via real reruns and adopted to center master; 1 warn left is concurrent readyfile drift. Waits on readyfile landing, then a reseal-plus-adopt finish.
- builder-fix-auditfold: PARTIAL O-008 F2P met (0 flags with 2 chars, 477-char description read), regression 6/6, check PASS. Review queued. Notes same fold bug in gates.py:158-162, out of scope, candidate next row.

## Rows
- No board change this round (no landing; PARTIALs recorded here). O-007 stays READY blocked-on-readyfile-land.

## Checks
- node sprint/check.mjs RESULT PASS 20 pass 0 warn 0 fail (lead reran 02:15Z).

## Held, not committed
- All builders' work uncommitted (reviews pending). Proof timestamp noise, keeper loop files, folded-mcp-forge research, packs/mcp-template, sprint/halt stays deleted.

## Next
- Collect 3 reviews plus ripgrep finish; land PASSes by path; then agentlint finish plus gates.py fold row.

## Retro (round 247, not due)
- None. Next retro due 250.
