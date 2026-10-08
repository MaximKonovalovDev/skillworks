# Pilot-240 stranger-run evidence (2026-10-06T23:09Z..23:20Z)

## make on small docs folder
- src: $env:TEMP\opencode\pilot-240\src\ (guide.md 320 B + advanced.md 244 B, 8 md headings)
- qa: $env:TEMP\opencode\pilot-240\pilot-240_qa.jsonl, 3 lines in {"q","must"} shape
- cmd: `python -m book2skill make --in <src> --name pilot-240-view --description "Use when testing the pilot stranger run" --qa <qa>`
- output: `extract folder, 599 chars, 2 files` / `split 1 chunks` / `index 1 records` / `build skills\pilot-240-view` / `eval 3/3 = 1.000 (gate 0.6)` / `audit 6 files, 356 tokens` / `fill SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text` / `receipt work\pilot-240-view\make.json`

## What the stranger gets (all files READ, not just listed)
- skills/pilot-240-view/SKILL.md: 338 bytes, frontmatter + one body line:
  `Built from owned sources. Start with chapters/notes.md, then glossary.md, patterns.md, cheatsheet.md. Use when the trigger topic matches this skill description.`
- glossary.md (41 B): `# Glossary / Fill terms while reading.`
- patterns.md (53 B): `# Patterns / Fill reusable patterns while reading.`
- cheatsheet.md (53 B): `# Cheatsheet / Fill one-page recall while reading.`
- chapters/notes.md (630 B): DOES hold the real extracted text of both source files verbatim.
- eval_report.json: total 3, passed 3, rate 1.0, graded_on skill.
- work/pilot-240-view/make.json: gate pass, placeholders [SKILL.md glossary.md patterns.md cheatsheet.md].
- Same defect class as the packet brief's 617-byte "Built from owned sources" skill (this instance is 338 bytes).

## Check sweep
- `python -m pytest tests/ -q`: 1 failed, 640 passed, 166 skipped in 74s. Only failure: tests/test_seat_guard.py::test_real_skills_tree_has_no_untracked_files (19 untracked files; includes this pilot's skills/pilot-240-view/ plus in-flight DR-1006-12 read-abort-guard skill files). Re-run after pilot scratch removal below.
- `node sprint/check.mjs`: RESULT PASS 20/0/0.
- `node C:/empire/center/arsenal.mjs --check skillworks`: RESULT PASS 13/0/0.
- `python tools/fleet_failures.py scan`: top classes with counts + plain error text, e.g. `172 edit: Could not find oldString...`, `109 bash: Unknown: ChildProcess.kill ...`, `96 bash: Tool execution aborted`, `82 websearch: StatusCode...`, `66 websearch: Missing key...` — readable, no defect.
- `python tools/pack_check.py packs/fleet-vol-1`: RESULT PASS (12 pass, 1 warning: price-evidence URLs no answer; store assets present; zips current).

## Cleanup
- skills/pilot-240-view/ removed after capture (pilot scratch, untracked; work/ output is gitignored).
- Export guard: `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing.

## Attribution (no new packet filed)
- The thin-skill observation (338-byte "Built from owned sources" SKILL.md,
  scaffold glossary/patterns/cheatsheet, eval 3/3 gate pass, no-target make
  exit 0) is the ALREADY-TRIAGED pilot-105 class: packet worked, direct-export
  refusal landed (abfc4e2, pinned by tests/test_export_scaffold_hold.py which
  passed in this run's full suite), no-target-make refusal parked under OWNER
  row K-54 awaiting owner verdict. Refiling would duplicate K-54.
- The seat-guard red (`test_real_skills_tree_has_no_untracked_files`) is
  working-tree state, not a HEAD defect: after pilot scratch removal it trips
  only on in-flight DR-1006-12 cure-seat files (skills/read-abort-guard/ +
  evals + tests/test_read_abort_guard.py, review packet
  builder-cure-readabort-review.md already queued) plus research/folded-mcp-forge/.
  A fresh clone at HEAD does not contain these. No packet.
- Net: pass complete, product verified as a stranger; zero new defects.
