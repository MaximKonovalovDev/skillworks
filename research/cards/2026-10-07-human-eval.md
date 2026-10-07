# Fast cash human eval lanes - 2026-10-07 (GO STEROIDS bulk round 1)

Goal: earn quick cash doing labeling and studies. Learn how good evals work.
Feed that back to the fleet eval skill.

Sources plus license:
- DataAnnotation at https://dataannotation.tech. Live board shows coding roles
  at 40 to 150 USD per hr, other expert roles 40 to 125, generalist 25 to 50.
  Header says expert rates up to 75 to 125 USD per hr. So the top rate holds
  for coding roles only. Proprietary platform. Account terms apply.
- Prolific at https://prolific.com. Pages say real cash, no gift cards,
  fair pay. The 12 USD per hr number was NOT found on the fetched pages
  on 2026-10-07, so treat it as unverified. Proprietary platform.

AI use ban: TRUE for both. Most paid tasks ban AI tools and remove workers
who paste from AI. Studies need a real human. Use only a human account.
Never pipe fleet output into their tasks. No task text in git.

Home: existing skillworks eval files (book2skill eval, tools eval score,
tests for eval grades and eval score, evals yaml). VISION.md sets the bar:
book in, eval 0.6 or more, skill_search over stdio.

Fixes: eval quality and trial pass rate. Learn rubrics plus pay for quality
plus human preference checks from these lanes. Copy that into eval prompts.

Net lines: about 60 to 120 lines. Small adapter plus docs. Redacted rubric
sample only. No new deps.

Proof:
- python -m pytest tests/test_eval_score.py tests/test_eval_grades_skill.py -q
- python -m book2skill make --help
- run eval on one skill before and after rubric change, show score delta,
  keep eval 0.6 or more. Fail if tests red or eval drops.

Effort S. Risk M. Slow onboarding, ID check, waitlist. Task supply varies.
Account ban if AI use suspected. Cash per task, not steady.
