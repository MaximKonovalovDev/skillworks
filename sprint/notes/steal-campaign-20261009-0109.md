# STEAL campaign 2026-10-09 01:09Z (lap 2)

Lap 2 (1 prior LAP line: audit 10-08). Started from ledger leftovers (audit S-cuts, lead2 S FOUNDs) plus prior steal ideas (LightningParse verified, eval/installer donors).

Baseline check before wave 1: PASS 20/0/0. After waves 1-4: PASS 20/0/0. Finish bars: 6/6 met (unchanged).

## Wave 1 hunt (10 researchers, read-only): 25 STEAL lines, all licences read live

| helper | STEALs | homes |
|---|---|---|
| R6 shop-proof | 3 (S,S,M) | export.py, pack_check.py, pack_build.py |
| usage-proof S1/S2/S6 | 2 (S,M) | finish_proof.py, skill_trial.py |
| domain packs R4 | 2 (S,M) | build.py |
| gate-lint | 2 (S,S) | gates.py, pack_check.py |
| leaderboard #5-15 | 2 (S,M) | _template, eval.py |
| arXiv eval | 2 (S,M) | eval_score.py, skill_trial.py |
| test shapes | 3 (S,M,M) | export.py, test_pipeline, test_pack_check |
| failure-class | 3 (S,M,S) | export.py, refresh.py |
| speed | 3 (S,M,S) | extract.py, index.py |
| ClawHub open copy | 3 (S,S,M) | export.py, install_fleet_skills.py, server.py |

## Wave 2 port (10 builders): 10/10 LANDED, each with test + attribution + steals.md line

BM25-lite (index.py, 0.57s->0.48s); reproducible ZIP (export.py, identical SHA256);
AST/TODO gate (gates.py); safe-archive guard (pack_check.py); bootstrap CI
(eval_score.py); median+p10 trials (skill_trial.py); fingerprint rebuild
(refresh.py); scope-router scaffold (build.py); hash-lock helpers
(install_fleet_skills.py); property tests (60 generated cases).

## Wave 3 hunt 2 (10 researchers): ~27 STEAL lines, licences read live

Retry (litl/urllib3/cenkalti MIT); schema (schema/jsonschema/msgspec);
oldest-ledger remainders (clawhub slug-gate, skills-manager trust signals);
CLI (typos/clap/ripgrep); release (image-size/standard-version/release-please);
reports (yasik/rich); observability (sentry/prometheus/mlflow); knobs
(vulture/dead-config/check-jsonschema); hand-rolled fns (django/packaging/
markdown-it-py); onboarding (superpowers MIT + 2 idea-only).

## Wave 4 port+verify (9 builders + 1 verifier): 9/9 LANDED, 0 reverted

Extract retry; receipt validators; did-you-mean; human audit block;
slug+fence rules; g18-lock dead-code cut (217->213); NEW knob_check.py
(4 dead keys surfaced); cover dimensions; export slug-version gate.
Verifier: check PASS 20/0/0, wave-4 30 passed, wave-2 29 passed.

Landed 19, reverted 0, skipped 0. Notes: wave-2 files were committed by the
loop auto-backup before wave 4 (clean re-land). Foreign untracked test files
from a parallel campaign left alone. No commits (parallel orchestrator).

## Asks (6 plans filed, most valuable first)

STEAL-CAMPAIGN-MCP-INSTALL, -SNAPSHOT, -LIGHTNING, -HASHWIRE, -ONBOARD, -CIGATE.
Next lap takes first: MCP install verb + snapshot harness lines above.
