# Decision template (own words)

Copy this shape into the report Choice block after review. Keep the same field names so reports stay comparable.

- title: short name of the call, 120 characters or less.
- situation: what is happening, in 2 to 5 plain sentences.
- scope: one of `team`, `multi-team`, `single-hard-problem`, `leader-support`.
- owner: the one person who carries the follow-up.
- review-date: shaped `YYYY-MM-DD`, the day the call is rechecked.
- options: numbered list, at least 2 real choices.
- risks: bulleted list, at least 1 line, or the line `- none listed`.
- choice: fill after review with the picked option, the reasons in one line each, and the next check.

Example field block the script writes:

```
# Decision: Migrate queue worker
archetype: tech-lead
scope: team
owner: dana
review-date: 2026-10-20
```

The script writes the header, the checklist, the options, and the risks. You write the choice.
