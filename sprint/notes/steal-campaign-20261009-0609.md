# STEAL campaign 2026-10-09 06:09Z (lap 5, 4 waves, 40 helpers)

Lap 5 (4 prior LAP lines). Started from leftovers: steal asks (mcp-install, snapshot, lightning, hashwire, onboard, cigate) + audit asks (queue-prune, spec-dup, harness-work) + lead2 (eval-registry, extract-gate, videopack). Inbox 43 open, filed none.

Baseline check before wave 1: PASS 20/0/0. After every wave: PASS 20/0/0.

## Wave 1 hunt (10 researchers, read-only): 17 STEAL lines, licences read live
| helper | STEALs | homes |
|---|---|---|
| S3 pack-sale | 2 (S,S) | pack_check.py |
| install verb | 1 (S) | install_fleet_skills.py |
| snapshot | 2 (S,S) | test_steal_snapshot, skill_trial |
| release CI | 1 (S) | g18-lock.py |
| validator lib | 1 (S) | pack_check.py |
| top domain repo | 2 (S,S) | build.py |
| arXiv eval | 1 (S) | eval_score.py |
| test shapes | 3 (S,S,M) | test_steal_mutation/snapshot/fuzz |
| check-failure fix | 2 (S,S) | run_spawn.py |
| speed | 2 (S,M) | index.py, extract.py |

## Wave 2 port (10 builders): 10/10 LANDED, test + attribution + ledger each
BM25 batch (index.py 0.0445s->0.0313s); snapshot goldens (0->2 frozen); pack drift gate (+2 S3 FAIL classes); install backup+dry-run (0->1); Wilson interval + paired lift (12/12 [0.7575,1.0]); thin-router scaffold (refs 1->3, SKILL 21 lines); mutation verdict (6 passed); lock-seed converge (false-STALE 1->0); trial golden gate; pwsh quoting guard (8 cases).

## Wave 3 hunt 2 (10 researchers): 19 STEAL lines, licences read live
Attested tier (sigistry MIT x2 + cartridge M); circuit-breaker + classified retry; cerberus ISC x3 (strict, collect-all, receipt schema M); clawhub publish-gate land-ready spec (export.py, deferred: foreign edits); click UsageError + django dry-run M; changelog automation x2; rich transient status; bmo metrics + CAV provenance M; toml-test knob corpus; frontcheck YAML errors + atomic-lru writes.

## Wave 4 port+verify (9 builders + 1 verifier): 9/9 LANDED, 0 reverted
Frontmatter errors (gates.py 0->7, stdlib-only); atomic refresh (torn 1->0); strict schema + collect-all QA (eval.py); CLI misuse hints + transient status (cli.py 5->0, 40+->10 lines); make stage timings (0->6); knob corpus (6+3 fixtures); changelog bump + Trust section (pack_build.py); attested tier (server.py 1->2); stdlib fuzz (200 seeds 0 crashes). Verifier: check 20/0/0, wave-2 41 passed, wave-4 31+17 passed.
Deferred (foreign edits on disk): extract.py camelot lattice + retry predicate, export.py publish-readiness. Deferred Ms for next lap: django dry-run, receipt schema, CAV provenance, inspect page, extract speed re-time.

Landed 19, reverted 0, skipped 2 (foreign-edit files). No commits (parallel orchestrator; loop auto-push lands by path).
