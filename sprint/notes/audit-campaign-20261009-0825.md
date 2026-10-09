# AUDIT campaign 2026-10-09 08:25Z (lap 7, 4 waves, 30 helpers)

Lap 7 (6 prior LAP lines). Leftovers taken first: runpairs L (re-measured, still open),
queue-prune/spec-dup/harness-work (protected or foreign-dirty, carried), onetext/
audit-desc/packgate/scoreproof/videopack/sprint-idx (lead's, untouched). Inbox 44 open,
filed none. Baseline check PASS 20/0/0; after every wave PASS 20/0/0. repo-standard
100/100 (folders 9.6/10: sprint README, protected, carried as S35).

## Wave 1 (10 researcher scouts)
| helper | result | file | proof | number |
|---|---|---|---|---|
| YAGNI | FOUND S | tools/eval_score.py --min-rate + spec_conformance evals-dir | rg 0 callers | 7 lines |
| dead code | FOUND S | book2skill/audit.py inside-guard 254-259 | ruff SIM223 | 4 lines |
| copy-paste | FOUND L | skills run_pairs/render 39x39 | rg -l counts | ~7800 lines |
| guessed APIs | NOOP | all SKILL.md fences verified real | --help/rg | 0 |
| dead flags | FOUND S | tools/pack_check.py FACTORY_PREFLIGHT read-never-set | rg 3 hits 0 sets | 1 key |
| over-abstraction | FOUND S | book2skill/export.py LAYOUTS/layout_for | rg 1 caller | 6 lines |
| missing tests | FOUND S | tools/extract_clean.py zero tests | rg tests exit 1 | 0 tests |
| prompt rot | NOOP | skills refs resolve | Test-Path | 0 |
| oversized | FOUND M | mcp_server/server.py 470, 4 more measured | Measure-Object | 5 files |
| slow paths | FOUND S | audit 0.86s startup-dominated | Measure-Command | 0.86s |

## Wave 2 (10 builders): 8 LANDED, 2 NOOP
audit.py 245->241 (7 passed); eval_score.py 427->420 --min-rate gone (9 passed);
test_extract_clean.py NEW 16 lines (2 passed); server.py -4 (4 passed);
eval.py 408->405 loud fail (2 passed); INDEX.md skill count 66+template (count proof);
skill_trial.py _trial_rates split (7 passed); part_score.py bogus-flag exit 2 (1 passed).
NOOP: export.py (edit denied, retried wave 4); requirements.txt (all 6 deps imported).

## Wave 3 (10 researcher-builders): 2 LANDED, rest FOUND/NOOP
pack_build.py loud-fail fix 392->395 (35 passed, 1 skipped);
finish_proof.py read-once 333->338 (19 passed). NOOP: README setup (no drift),
extract_clean (no smell). FOUND: board 2 DONE-open rows S (protected);
queue 4 stale claims + orphan SCOUT lock + empty running/ M with reset rule (protected);
README out/-vs-dist S; gates.py lazy-import ~0.25s M (foreign-dirty);
mcp_schema single-session split S; 3 abort-guard SKILL.md overlap M.

## Wave 4 (5 land + 5 verify): 4 LANDED, 1 correct SKIP, all green
README.md out/->dist/ (path proof); test_mcp_schema.py 1.39s->0.55s (4 passed);
export.py 288->282 LAYOUTS/layout_for (book_to_skill 2 passed, export_targets 13 passed);
server.py 466->464 (5 passed). SKIP: finish_proof 2nd cut (foreign hunk).
Verifiers: check 20/0/0; A 18 passed; B 25 passed; C 43 passed 1 skipped;
D min.rate/gone, inside-gone, skills 67 = INDEX 66+template; E standard 100/100,
JUNK/ROOT/BIGDOCS/NAMES pass, sprint folder only gap.
Note: test_export_guard.py 20 failed is pre-existing (fails in _refuse_same_version:262,
untouched by our hunk; lap-4 report recorded same-version fails before this campaign).

## Reverted / skipped
Reverted 1 (mine): skill_trial.py feature-creep (+~90 lines eval_metadata/timing,
no test referenced it) cut back to the _trial_rates split only (+8/-3, 11 passed,
check PASS). Skipped: pack_check/fleet/gates/split_chapters (foreign-dirty);
spec_conformance/split_chapters (denied lap 4, not retried); board/queue/.opencode/
sprint writes (protected); export_guard failures (pre-existing, not ours).

## Asks carried (inbox full, none filed; next lap takes first)
Board 2 DONE-open DR-1006-6/DR-1006-5; queue reset+ready rule; gates.py lazy-import;
3 abort-guard overlap; runpairs L; packsplit L; S52-S55; knobs x4; researcher.md:44;
S35 sprint README; S130-S133, S34.
Net tracked on campaign files: +62/-65 (net -3) + 1 new 16-line test; check green.
