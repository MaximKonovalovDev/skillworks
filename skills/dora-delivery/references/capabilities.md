# DORA measures and capabilities, in our own words

Paraphrased notes from the DORA research program at https://dora.dev/ (CC-BY-4.0; see `sources.md`). Short names and numbers are reused with credit; every sentence below is our own.

## The four measures

- Deploy rate (`deploy_per_week`): how often code reaches real users, counted as deploys per week. More frequent, smaller releases are easier to test and to roll back.
- Lead time (`lead_hours`): how long one change takes from commit to running live, in hours. Short lead time means the path from idea to user is clear of waits.
- Failure share (`fail_pct`): how many changes fail in production and need a fix or rollback, in percent from 0 to 100. Lower is better.
- Restore time (`restore_hours`): how fast service recovers after a bad change, in hours. Fast restore means good detection, quick rollback, and practiced repair.

## Simplified grade bands used by `scripts/dora_delivery.py`

These bands are simplified for coaching, not the official DORA cutoffs:

- deploy: elite at `7 per week` or more, high at `1 per week` or more, medium at `0.25 per week` or more, else low.
- lead: elite under `24 hours`, high at `168 hours` or less, medium at `720 hours` or less, else low.
- fail: elite at `15 pct` or less, high at `30 pct` or less, medium at `45 pct` or less, else low.
- restore: elite under `24 hours`, high at `168 hours` or less, medium at `720 hours` or less, else low.
- overall: the `weakest link`, the lowest of the four grades.

## Capabilities that lift the grades, grouped

Delivery habits:
- version control: every change tracked in one shared history with small, linked commits.
- trunk-based work: short-lived branches merged to the trunk at least daily, flags hiding unfinished work.
- continuous integration: each merge builds and runs fast tests at once, broken builds fixed first.
- test automation: a fast, trusted suite developers run before review, slow end-to-end tests kept few.
- deployment automation: one tested path ships to production with no hand steps.

Architecture habits:
- loosely coupled architecture: services change and ship alone without lock-step releases.
- small batches: work split so each release is reviewable in one sitting.
- monitoring and feedback loops: production health and user signals reach the team within hours.

People habits:
- documentation: setup, run, and repair notes kept next to the code and updated with each change.
- security shift-left: security checks run with the build, not as a gate at the end.
- empowered teams: the team picks its tools and can ship without outside approval.
- learning reviews: each failure ends with one written fix, not blame.

## How to use the checklist

Measure the four inputs first, grade them, then pick the weakest metric and adopt one capability from its group. Re-measure after two weeks and keep the change only if the grade moves.
