# Human eval rubric sample - O-013 (REDACTED, own words only)

Date read live: 2026-10-07. No vendor task text in git. Ever.

Sources (public pages only, proprietary platforms, account terms apply):
- DataAnnotation: coding roles 40-150 USD/hr, expert roles 40-125, generalist
  25-50. Proprietary. AI-use ban TRUE: most paid tasks ban AI tools and
  remove workers who paste from AI. Studies need a real human.
- Prolific: real cash, fair pay (the 12 USD/hr number was NOT found on the
  fetched pages 2026-10-07, treat as unverified). Proprietary. AI-use ban TRUE.

Rule honored: never pipe fleet output into their tasks. Human account only.
This file carries a rubric rewritten in our own words. No question text,
no answer text, no prompt text from either platform appears here or in any
commit.

## Rubric learned (own words, 5 checks, each pass/fail)

1. Correct: the answer names the exact tokens the question asks for.
2. Whole: every required token is present, none missing.
3. Clear: one reading, no guesswork, steps in order.
4. Safe: no secret, no key, no private path, no copied book text.
5. Shaped: the answer fits the asked shape (line, list, or run output).

Grade per item (maps to tools/eval_score.py):
- 1.0 all required tokens present (pass).
- 0.5 some but not all present (partial, needs a fix note naming the miss).
- 0.0 none present (hard fail).
Each item carries one reason line naming what was found or missed.
Ship rule unchanged: export gate rate 0.6 or more (book2skill/eval.py,
book2skill/export.py GATE 0.6).

Pay-for-quality take: pay per good judgment, not per word. Two graders
agree before a sample counts. Preference check: show two answers blind,
pick the one a stranger can act on in 5 minutes.

## Grade delta (before and after this rubric note, skill pipe-run)

Command (offline, no model):

    python tools/eval_score.py report --skill pipe-run

- Before: qa 11, rate 1.0 +/- 0.0, weighted 1.0, failure 0.0.
  Trials 12 runs, with 1.0, without 0.1667, lift 0.8333 +/- 0.1124.
- After: same numbers (this row changes no eval code, only adds this
  redacted sample). Rate 1.0 keeps eval 0.6 or more. RESULT PASS.
  Proof at 2026-10-07T09:53Z, fingerprint
  f1488e7033a10f1b75cc96ab1cdfd3b22e322e67d30c57197daab936d1ae4b6a.

Proof this row lands:
- python -m pytest tests/test_human_rubric.py tests/test_eval_score.py
  tests/test_eval_grades_skill.py -q green.
- node sprint/check.mjs PASS.
