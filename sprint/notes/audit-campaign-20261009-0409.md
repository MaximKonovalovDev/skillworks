# AUDIT campaign 2026-10-09 04:09Z (lap 4, 4 waves, 40 helpers)

Lap 4 (3 prior LAP lines). Started from leftovers: lap-1 S-cuts (all since landed), steal/lead2 asks (mcp-install, snapshot, eval-registry, extract-gate, videopack — untouched, still lead's).
Baseline check: PASS 20/0/0. After every wave: PASS 20/0/0. repo-standard 97/100 -> 100/100. Loop auto-backup f552ed3 committed waves 2-3 files by path.

## Wave 1 (10 researcher scouts)
| helper | result | file | proof | number |
|---|---|---|---|---|
| YAGNI | FOUND S | mcp_server/server.py dead `_parse_skills_dir_override` | rg def-only | 7 lines |
| dead code | FOUND S | tools/edit_guard.py 2 dead locals | ruff 2xF841 | 2 lines |
| copy-paste | FOUND S | read_rows x3 tools files | rg 3 hits | ~12 lines |
| guessed APIs | ASK | .opencode/skills/skill-eval-harness/SKILL.md:17 (protected) | eval --help | 1 doc |
| dead flags | NOOP | knob_check.py already surfaces all 4 | EXIT:1 | 0 |
| over-abstraction | FOUND S | book2skill/cli.py index_mod_split | rg 2 hits | ~4 lines |
| missing tests | NOOP | 20 hottest files covered | rg | 0 |
| prompt rot | L+M+S | researcher.md:44, flax-forge-ops, sprint.md:31 | Read/Test-Path | 3 |
| oversized | FOUND L | tools/fleet_failures.py lanes split | 511 lines | L |
| slow paths | FOUND M | extract.py markitdown ~8s | Measure-Command | ~8s |

## Wave 2 (10 builders): 6 LANDED
server.py (5 passed, 1->0), edit_guard.py (ruff clean, 4 passed, 2->0), cli.py (20 passed, 1->0), eval.py:330 swallow (3 passed, 5->4), eval_score.py:264,283 never-fail (exit 1 shown, 9 passed, 1->0), audit.py:168,223 split (9 passed, 106->97). NOOP: read_rows (bodies differ: tolerant vs strict — NOT a dupe, dropped), markitdown already lazy (1.39s, 29 passed), security clean, requirements pin FOUND S.

## Wave 3 (5 scout + 5 build): 4 LANDED
freud notes.md split 1->4 files (bigdocs 0/3->3/3, 16 passed); extract.py:20,385 speedup (1.36/2.15/1.91->1.70/1.08/0.86s, 9 passed); export.py skill_version 2->1 (1 passed); requirements pytest==9.1.1 (9 passed, 6->5 loose). NOOP: trim clean (0 DONE rows), sprint README keeper-denied. FOUND: README export drift S, spec_conformance dup S (denied), split_chapters skips S (denied), queue rot 2S+2M.

## Wave 4 (9 land + 1 verifier): 5 LANDED, 0 reverted
README export drift (doc-only; export-test 21 failures pre-existing, identical set); flax-forge-ops --check 3->1 slots; find-vol1 49->48 (5 passed); adopt_repo test 12->11 (4 passed); distill.py:175 67->59 (22 passed). Denied (asks): spec_conformance, split_chapters. FOUND: extract-engines M, README no-install S. Verifier: check PASS 20/0/0, 23 passed, 216 passed +1 pre-existing pwsh-proof fail, export 18+1 pre-existing same-version fail.

## Reverted / skipped
Reverted 0. Skipped: pack_check/fleet/adopted/split/fastmcp/mcp_rank (loop-active foreign edits); adopt_engine_builder (no test cover); AGENTS/opencode/queue/sprint writes (protected/denied).

## Asks: 6 plans filed (most valuable first)
AUDIT-CAMPAIGN-QUEUE-PRUNE, -SPEC-DUP, -SKIP-JUSTIFY, -HARNESS-WORK, -SPRINT-SEEDS, -README-INSTALL. Correction: S54 done-when should read "done when: the doc example runs clean with --work accepted". Carried (already open, not re-filed): runpairs L, packsplit/fleet-lanes L, knobs x4, researcher.md:44, sprint README, forge/video/registry/gate asks.
Net: +78/-3544 lines on disk (freud split), check green, repo-standard 100/100.
