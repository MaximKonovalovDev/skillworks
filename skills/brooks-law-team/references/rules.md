# Rules in full

Clean-room notes for `brooks-law-team`. Own words. Ideas credited to Fred Brooks.

## 1. Count channels as n*(n-1)/2

Every pair of people needs a talk line. Pairs for n people: n*(n-1)/2.

| n | channels |
|---|---|
| 1 | 0 |
| 2 | 1 |
| 3 | 3 |
| 4 | 6 |
| 5 | 10 |
| 6 | 15 |
| 7 | 21 |
| 8 | 28 |

A team of 5 has 10 channels. Grow it by 3 late people to 8 and the count jumps
from 10 to 28, which is 18 new channels to feed. The script quotes both numbers
before it decides, so nobody votes to add people blind.

## 2. HOLD late additions on a short clock

Late staff pay twice: training takes the old hands away from the work, and the
new channels in section 1 add talk on top. So when weeks_left is 6 or less and
the leftover work is not splittable, adding people ships later, not sooner.

- `late_add` over 0 plus `weeks_left` 6 or less plus `splittable` false gives HOLD with reason late staff on a short clock.
- The same `late_add` with `weeks_left` over 6, or with `splittable` true, can still PLAN when the team stays at 7 or less and the integrity gate passes.

## 3. One chief plus support, split over 7

One chief does the key work. The rest support: tools, tests, docs, build. Nobody
else touches the core. Up to 7 people this fits one team as 1 chief + rest support.
Over 7 the talk cost in section 1 eats the gain, so split into a second team.

- 7 or less: surgical shape 1 chief + rest support, for example 1 chief + 4 support at n=5.
- 8 or more (counting late_add): HOLD with reason team over 7 split in two.

## 4. Integrity gate: 1 or 2 owners PASS

One small holder must own the design, or every team bends it their own way and
the product stops looking like one thing. The gate reads `design_owners`.

- 1 or 2 owners: integrity PASS.
- 3 or more: integrity FAIL and HOLD with reason design owners keep 1 or 2.

## Worked examples

- PLAN: n=5, late_add=0, weeks_left=10, design_owners=1 gives PLAN n=5 channels=10 integrity PASS surgical 1 chief + 4 support.
- HOLD late: n=5, late_add=3, weeks_left=4, design_owners=1, splittable=false gives HOLD n=5 channels=10 to 28 integrity PASS reason late staff on a short clock.
- HOLD owners: n=4, late_add=0, weeks_left=10, design_owners=3 gives HOLD n=4 channels=6 integrity FAIL reason 3 design owners keep 1 or 2.
- HOLD split: n=8, late_add=0, weeks_left=10, design_owners=1 gives HOLD n=8 channels=28 integrity PASS reason team over 7 split in two.

The tool does not estimate ship dates and does not split tasks for you.
