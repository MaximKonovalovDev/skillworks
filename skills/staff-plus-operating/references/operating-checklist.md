# Operating checklist (own words)

Six lines the report checks every time. Each line reads `PASS` or `FAIL`. A report ships with a FAIL on the page, but the weak line is visible.

- direction-written PASS: title and situation are both non-empty. FAIL when either is blank.
- owner-named PASS: one owner string is named. FAIL when blank.
- options-listed PASS: at least 2 non-empty options. FAIL when fewer.
- risks-listed PASS: at least 1 risk. FAIL when none is listed.
- review-dated PASS: review date is shaped `YYYY-MM-DD`. FAIL on any other shape.
- scope-matched PASS: scope is one of `team`, `multi-team`, `single-hard-problem`, `leader-support`. FAIL is impossible here because a bad scope is refused before the report is written.

Weekly use: run the same 6 lines on Friday, file the misses, and carry at most 2 misses into next week.
