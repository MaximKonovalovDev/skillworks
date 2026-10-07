# w7-final1: final rate + sell/reuse

Date: 2026-10-06. Loop OFF. Scope: `packs/w7-final1.md` only. No code copied.

## Final rate (rubric: useful, small, provable)

- `server-template` (w4-fix1, w6-rich1): 8/10. Three tools live, selftest passes, deny ok. Loses: no transport test, no outside run yet.
- `sec-gate` spec (w4-enrich1, w4-reuse1, w5-reuse1): 6/10. Three checks plus 5 cases, skillworks named user. Loses: spec only, no measured block yet.
- `gw-router` (w2-steal T3): 3/10. Spec only, dropped in w4-slim1. Right call.
- Overall: 6/10. One live slice, one spec, one cut.

## Sell

Sell nothing yet. The 3-tool demo is the first sellable after one outside run.

## Reuse

Reuse now: all repos copy `server-template` for new tools. skillworks runs the 5 sec-gate cases as a checklist. fp-research supplies poison patterns only, own targets only.

## Done when

Template has one outside run. Sec-gate plan lists the 5 cases by name.

## Proof

`node sprint/check.mjs` in `C:/Users/me/Desktop/mcp-forge`.
