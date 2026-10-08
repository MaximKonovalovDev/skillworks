# AUDIT campaign 2026-10-08 14:40Z (halted after wave 1)

Halt present (`sprint/halt`: paused by Maxim 10:24Z). Wave 1 scout only; no land waves. No commits (parallel orchestrator never commits).

Baseline check before wave 1: PASS 20/0/0. After wave 1: PASS 20/0/0. No edits by this campaign; diff is the loop's own files only.

Lap 1 (no cycle-ledger yet). Prior lap (lead2 10:56Z) landed 0, left S FOUNDs unlanded; this lap re-confirmed two of them below.

## Wave 1 (10 researcher scouts, read-only)

| helper | result | file | proof | number |
|---|---|---|---|---|
| YAGNI | FOUND S | tools/g18-lock.py dead is_exact + RANGE_HINT | rg is_exact/RANGE_HINT: def only | 2 dead names |
| dead code | FOUND S | book2skill/split_chapters.py dead is_fence | rg is_fence: def only | 3 lines |
| copy-paste | FOUND L | run_pairs cloned in 37 run_*.py, render in 39 pairs_to_md.py | rg def run_pairs: 37 files | ~120 lines x37 |
| guessed APIs | FOUND S | evals/README.md eval call omits required --work | b2s.py eval --help: --work required | 1 stale doc |
| dead flags | FOUND L | knobs paid_mode set-never-read; repeat_cap/min_free_gb/fresh_ctx_k read-never-set | rg both directions | 4 keys |
| over-abstraction | NOOP | b2s/part_score/gen_run_pairs/new_skill all real | rg callers | none |
| missing tests | NOOP | 4 hot files all test-covered | rg tests | none |
| prompt rot | FOUND L | .opencode/agents/researcher.md:43 contradicts AGENTS.md rule 0 | read both | 1 contradiction |
| oversized | FOUND M | tools/pack_check.py 533 lines (fleet 511, adopted 507, test 400, finish 285) | Measure-Object lines | 533 max |
| slow paths | FOUND S | check vision import dominates ~10s over node baseline | Measure-Command 13.4s | ~10s |

Landed 0 (scouts read-only; S cuts filed as FOUND for wave 2).
Reverted 0. Skipped: waves 2-4 not run (halt returned True mid-campaign).
Asks: 4 plans filed (see below); S leftovers ride the ledger.

## Asks filed
- AUDIT-CAMPAIGN-runpairs: dedupe run_pairs across 37 skill scripts
- AUDIT-CAMPAIGN-packsplit: split tools/pack_check.py 533 lines
- AUDIT-CAMPAIGN-knobs: resolve 4 dead knob keys (protected files)
- AUDIT-CAMPAIGN-researcher: fix researcher.md vs AGENTS.md rule 0 (protected)
