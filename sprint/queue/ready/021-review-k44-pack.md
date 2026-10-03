---
role: judge
title: Review K-44 SELL-FIRST-PACK (freud listing + Vol 0 + marketplace fields)
---

Goal: Independent review of the builder's K-44 PARTIAL before the lead commits: `skills/freud-dream-psychology/listing.md` + `vol0-sample.md` + `skills/progit-branching/listing.md` marketplace fields.

Scope: the two new freud files, the progit listing diff, row K-44 done-when in `sprint/board.md`. No code changes by the judge. Note: `sprint/steals.md` marketplace line is marked landed by the lead on commit.

Proof: re-run `python -m pytest tests/ -q` and `node sprint/check.mjs` yourself (after the vision-repair packet clears the current 19/2 FAIL); check listing names source + PD basis + translator/edition year + price URLs, Vol 0 sample exists with no paid-Vol-1 price line, ZIP regenerates with SKILL.md at root, PREP-ONLY with no Live listing URL, gate `rate < 0.6` untouched. At most 15 lines: PASS (lead may commit by path) or FAIL (one repair back to the builder, exact lines).

Stop: S 20 min. End: `RESULT: PASS|FAIL - <one line> | proof: <commands>`.
