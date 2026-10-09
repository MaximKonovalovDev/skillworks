# STEAL campaign 2026-10-09 09:50Z (lap 8, 3 waves, 30 helpers; wave 4 held)

Lap 8 (7 prior LAP lines). Leftovers taken first: steal-lap5 deferred
(twine refusal, scorio Bayes, plugship/skillhub, honorbox listing, Tip4Serv
schemas, django dry-run, receipt schema, CAV provenance, camelot lattice) +
audit asks (board-DONE, queue-reset, gates-lazyimport). Inbox 45 open, filed none.
Baseline check before wave 1: PASS 20/0/0. After waves 1-3: PASS 20/0/0.

## Wave 1 hunt (10 researchers, read-only): 16 STEAL lines, licences read live
| helper | STEALs | home |
|---|---|---|
| R6 shop proof | 3 (M,S,S) | pack_build.py / pack_check.py |
| S3 finish bar | 1 (S) | install_fleet_skills.py |
| R6 publish gate | 2 (S,S) | export.py (deferred: foreign edits) |
| gates.py core job | 2 (M,S) | gates.py |
| top domain repo | 1 (S) | build.py |
| arXiv eval | 1 (S) | eval_score.py (deferred: foreign edits) |
| test shapes | 2 (S,S) | tests/test_steal_importquiet|logassert |
| export-guard fix | 1 (S) | export.py (deferred: foreign edits) |
| speed | 1 (S) | index.py |
| competitor copy | 3 (S,S,S) | mcp_server/*helpers |

## Wave 2 port (10 builders): 10/10 LANDED, test + attribution each
BM25 eager postings (index.py 0.0071s->0.0029s, bit-identical); fenced-only
grader (build.py false-pass 4->0); strict frontmatter subset (gates.py 0->6);
storefront-drift gate (pack_check.py S3 FAIL +1); pinned digest order
(install_fleet_skills.py 1->0); lockfile helper (new, 0->2 locked);
preview-then-install (new, 0->3 fields); import-quiet gate (1->0);
ordered log-assert (0->7); pre-install scan verdict (0->1).
Ledger: 10 lines appended to sprint/steals.md by orchestrator (one owner rule).

## Wave 3 hunt 2 (10 researchers, read-only): 15 STEAL lines, licences read live
stamina giveup-predicate (extract.py); jschon Result-tree receipt check
(make.py); twine land-ready spec with golden vectors (export.py); gh help +
click exit codes (b2s.py); changelog-fragments bump + towncrier base-ref
(g18-lock.py); semchunk PR#24 guard (split_chapters.py); aiologger/logging_tree
(make.py, 2nd home); hydra dataclass schema + ciri taxonomy (knob_check.py);
github-slugger/slug-rs slugify (new_skill.py); addyosmani quickstart shape
(b2s.py --help, idea-only).

## Wave 4 NOT run: stop switch set
sprint/halt exists (pressed mid-wave-3 check). extract.py + make.py also went
foreign-dirty during wave 3, so their ports would have skipped anyway.
No wave-4 landings; nothing to revert (check green, no edits since wave 2).

## Deferred for next lap (all hunted, land-ready, most valuable first)
1. twine two-stage duplicate refusal -> export.py (S, golden vectors ready)
2. stamina giveup-predicate -> extract.py (S, classified retry)
3. jschon receipt Result-tree -> make.py (S, structured errors)
4. hydra dataclass schema -> knob_check.py (S, kills hand KNOWNS)
5. slugify mirror -> new_skill.py (S, 10 lines)
6. gh grouped help + click exit 2/1 -> b2s.py (S x2)
7. semchunk validate-first guard -> split_chapters.py (S)
8. scorio Bayes@N -> eval_score.py (S, needs clean file)
Landed 10, reverted 0, skipped 0. No commits (parallel orchestrator).
