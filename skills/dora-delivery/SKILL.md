---
name: dora-delivery
description: Use when grading delivery speed and stability from a JSON file with the four DORA numbers: deploy rate, lead time, failure share, restore time plus capability checklist.
version: 0.1.0
author: skillworks
license: CC-BY-4.0 (DORA text), MIT (this skill's scripts)
---

# Delivery grading with the four DORA metrics

Grades delivery speed and stability from the four DORA measures, in your own words, plus the capability checklist that lifts them. Headless: no network, no prompts. Reads one JSON file with the four numbers and writes one JSON grade file.

The four measures are deploy rate, lead time, failure share, and restore time.

## Use it

Run `scripts/dora_delivery.py` from this skill's folder, or give its full path:

```powershell
python scripts/dora_delivery.py --input <path> --out <path>
```

The first word of stdout is the answer:

- `GRADE <overall> deploy <d> lead <l> fail <f> restore <r>`: exit 0. Wrote the grade record to the `--out` file.
- `ERROR ...`: exit 2, nothing written. Causes, one clause each: input file missing, input not JSON, a key missing, a value out of range, `--out` is a directory.

## Rules

- The input JSON must carry exactly these four keys with numbers: `deploy_per_week` (deploys per week, 0 or more), `lead_hours` (commit to live in hours, 0 or more), `fail_pct` (failed changes in percent, 0 to 100), `restore_hours` (fix time in hours, 0 or more).
- Elite needs all four at once: `7 per week` or more deploys, under `24 hours` lead time, at most `15 pct` failures, under `24 hours` restore. High needs `1 per week` or more, `168 hours` or less, `30 pct` or less, `168 hours` or less. The overall grade is the `weakest link`: the lowest of the four metric grades.
- This tool does not read git history and does not set an official DORA rank: it only grades the numbers you pass, so measure the four inputs first. It does not call a model and does not use the network.

Detail on each measure and the capability checklist lives in `references/capabilities.md`. Where the ideas come from lives in `references/sources.md`.
