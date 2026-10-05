---
role: judge
title: review edit-unique skill (DR-1004-4 cure on disk)
chain: review
of: builder-cure-r1
writer: builder
attempt: 1
origin_title: cure smith edit-unique DR-1004-4
---

Review builder-cure-r1 (claim DR-1004-4 2026-10-05T10:11Z), built by builder. Its record: claim line in sprint/queue/claims.txt for skills/edit-unique plus evals/edit-unique_qa.jsonl plus tests/test_edit_unique.py. Rerun its proof yourself, read its diff, check DR-1004-4 done-when as written (partly is FAIL). You never edit.

Goal: judge the edit-unique skill as it stands on disk (DR-1004-4 ambiguous-oldString class, 28 misses/48h).

Scope: skills/edit-unique/ (SKILL.md, references/pairs.json, references/pairs.md, references/errors.md, references/sources.md, references/live-proof.json, references/trial-proof.json, scripts/run_unique.py, scripts/pairs_to_md.py), evals/edit-unique_qa.jsonl, evals/edit-unique_trials.jsonl (read-only sheet), tests/test_edit_unique.py, book2skill/gates.py (FLEET_SKILLS edit-unique line), tools/install_fleet_skills.py (FLEET edit-unique line), THIRD_PARTY_NOTICES.md (edit-unique credit line), team/p3.md (2026-10-05T10:17Z tried line).

Proof: 1. Skill: SKILL_LIVE=1 python -m pytest tests/test_edit_unique.py -q ends 6 passed; python tests/live_proof.py edit-unique ends proven; python tools/skill_trial.py grade --skill edit-unique prints runs 12 with_rate 0.8+ lift 0.3+ RESULT PASS. 2. Always: python -m pytest tests/ -q and node sprint/check.mjs equal or better than before (green HEAD 434 passed 116 skipped, check 20/0/0); Get-ChildItem skills -Recurse -Directory -Filter export prints nothing and no path over 240 chars; git diff plus untracked has no other repo path/text/number, no secret; only owned files; no weakened gate, no edited QA; ONE REAL THING: python tools/fleet_failures.py round-line --check shows proven 13 trials 7 (was 12/6).

Stop: M 30 min; judge only, no edits; never commit. End with VERDICT: PASS|FAIL|BLOCKED plus what changed, checks before/after with numbers and the one real thing, and how to revert, in at most 15 lines.
