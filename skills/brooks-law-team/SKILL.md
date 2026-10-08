---
name: brooks-law-team
description: Check a team plan for Brooks-law risk before adding people late: count channels, shape a surgical team, gate design integrity. Use when staffing or replanning a late project and deciding whether to add people.
license: MIT
---

# brooks-law-team

Check a team plan before you add people to a late project. Headless: no network, no prompts. It counts talk channels as n*(n-1)/2, shapes a small chief-led team, and gates the design on one holder.

Ideas credited to Fred Brooks, written here in our own words. No book text is quoted or copied.

## Use it

Run `scripts/brooks_law_team.py` from this skill folder, or give its full path:

```powershell
python scripts/brooks_law_team.py --input <plan.json> --out <report-dir>
python scripts/brooks_law_team.py --help
```

The plan file is JSON with `n` (current people, int 1 or more), `design_owners` (people who can approve design, int 1 or more), `weeks_left` (weeks to the date, number 0 or more), plus optional `late_add` (people you would add late, int 0 or more, default 0) and `splittable` (true when the leftover work splits cleanly with no training, default false).

The first word of stdout is the answer:

- `PLAN n=<n> channels=<c> integrity PASS`: exit 0. The team can go as shaped. Writes `report.json` plus `plan.txt` into `--out`.
- `PLAN n=<n> channels=<c> to <c2> integrity PASS`: exit 0. Same, with the grown channel count when `late_add` is over 0.
- `HOLD n=<n> channels=<c> integrity FAIL`: exit 0. Do not go: fix the plan first, then re-run. Writes `report.json` plus `plan.txt` into `--out` with the reasons.
- `HOLD n=<n> channels=<c> to <c2> integrity PASS reason late staff on a short clock`: exit 0. Same HOLD family for late-add risk or a team over 7, even when integrity passes.
- `ERROR ...`: exit 2, nothing written. Missing plan file, bad JSON, bad value (n below 1, late_add below 0, weeks_left below 0, design_owners below 1, splittable not true or false), `--out` is a file, or `--out` is the input file itself.

## Rules

- Count channels as n*(n-1)/2 for the current team and for the grown team, and quote both numbers before deciding. A team of 5 has 10 channels; a team of 8 has 28.
- HOLD late additions on a short clock: when weeks_left is 6 or less and the work is not splittable, late staff adds training plus new channels and ships later, so the answer is HOLD with reason late staff on a short clock.
- Keep one chief plus support and split over 7: 1 chief + rest support on one team up to 7 people, over 7 split into a second team. A team over 7 is HOLD with reason team over 7 split in two.
- Pass the integrity gate with 1 or 2 design owners only; 3 or more is HOLD with reason design owners keep 1 or 2, because one small holder must own the design.
- This tool does not estimate ship dates and does not split tasks for you; it only scores the plan you hand it.

Channel counts, gate limits and worked examples: `references/rules.md`.
