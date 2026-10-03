# Hunt lane — zero-token skill-market hunt [STEAL-PATTERN-1001] (K-05)

Date: 2026-10-03 | Owner role: researcher | Pattern: the 8-repo research pattern
(zero-token hunt lane + topic list + Steal map reads, oldest-first).
Scope: `research/hunt.md` + Steal map S01-S20 reads only. No code, no VISION edits.
Proof: this file exists with discover-style queries + topic list + oldest-first
read order, plus `node C:/Users/me/Desktop/center/vision-check.mjs skillworks`
no FAIL and `node sprint/check.mjs` PASS.
Stop: S 25 min per hunt pass — file cards + write the Last-read date back, no implementation.

## Zero-token rules (no tokens spent on browsing)

1. No network calls on a hunt pass: read only local ground — `VISION.md`
   (Scorecard + Parts + Steal map S01-S20), `research/cards/`, `research/INDEX.md`.
2. Discover-style queries below are pre-built search strings for the next
   networked sweep (researcher or center discover); a zero-token pass only
   picks the next query, never runs it.
3. Each pass reads the Steal map row read longest ago (oldest-first, tie-break
   by lowest ID), judges its cards against the Research contract, and writes
   its Last-read date back to `VISION.md`.
4. Unknown stays UNKNOWN. No invented URLs or licenses. Duplicates merge into
   one experiment (see `research/INDEX.md` merges).

## Discover-style queries for skill markets (12, Scorecard-gap ordered)

Queries are built from the Scorecard gaps (biggest gap to the best first:
R5/R6 0%, then R4/R2). Each names its Steal row so a sweep can start at the
oldest unread row that matches.

| # | Query (discover-style, run by the next networked sweep) | Serves | Steal row |
|---|---|---|---|
| Q1 | `agent skill marketplace SKILL.md bundle downloads stars verified` | R4/R5 shop format | S01 ClawHub |
| Q2 | `agent skills discover trending install count preview before install` | R4 domain gap | S02 SkillsGate |
| Q3 | `skill-as-API vs MCP stdio skill_search serving` | R3 MCP delivery | S03 Skrun |
| Q4 | `agent skills eval framework pass fail metric registry` | R2 eval gate | S04 Evos |
| Q5 | `AGENTS.md sync multi-target export skill` | R5 export targets | S05 agentic-prompt-sync |
| Q6 | `progressive disclosure SKILL.md references layout agent` | R1 pipeline build | S06 superpowers |
| Q7 | `real-engineer skill shape coding agent` | R1/R4 packs | S07 mattpocock/skills |
| Q8 | `agent memory instincts harness skill use` | R1 skill use | S08 ECC harness |
| Q9 | `agent loop calling skills tool use` | R3 agent loop | S09 hermes-agent |
| Q10 | `book to skill chunk index pipeline receipts` | P1 pipeline | S10 book-to-skill |
| Q11 | `skill export per-target layout claude codex opencode gemini` | R5 export | S12 Skill_Seekers |
| Q12 | `skill listing price gumroad itch demo gif sample` | R6 shop proof | S19/S20 Gumroad + MoneyPrinterTurbo |

License gate for any networked follow-up: code may be copied only under MIT,
Apache-2.0, BSD, zlib or CC0 with the license read live; GPL/AGPL/proprietary
is ideas-only, never pasted (per the Research contract + center discover rules).

## Topic list (8 hunt topics, each tied to Steal rows)

1. Skill markets — what sells, what format wins (S01, S02, S19).
2. Domain gap — where non-dev packs beat dev wrappers (S02, S17, S18).
3. MCP serving — stdio skill_search vs API vs desktop Discover (S01, S03, S09, S13, S15).
4. Honest eval — Q&A gate that blocks ship (S04).
5. Export sync — one build to 4 targets without drift (S05, S12, S14).
6. Skill layout — SKILL.md + references shape agents love (S06, S07, S08).
7. Pipeline receipts — extract-to-export timing + fingerprint refresh (S10, S11, S16).
8. Shop proof — listing, Vol 0 sample, GIF demo, honest 0-sales counter (S19, S20, P5).

## Oldest-first read order over the Steal map (20/20 complete)

All 20 rows are dated 2026-10-03 in `VISION.md` today, so oldest-first falls
back to lowest-ID-first. Next networked sweep starts at the head and writes
each row's Last-read date back after judging.

Read order (oldest-first): S01, S02, S03, S04, S05, S06, S07, S08, S09, S10, S11, S12, S13, S14, S15, S16, S17, S18, S19, S20.

| Order | ID | Kind | Sources | Part | Last read |
|---|---|---|---|---|---|
| 1 | S01 | competitor | ClawHub skill market | R4/P5 | 2026-10-03 |
| 2 | S02 | competitor | SkillsGate index (45k skills) | R4 | 2026-10-03 |
| 3 | S03 | competitor | Skrun skill-as-API | R3 | 2026-10-03 |
| 4 | S04 | competitor | Evos domain skills + eval suite | R2/R4 | 2026-10-03 |
| 5 | S05 | competitor | westonplatter/aps (agentic-prompt-sync) | R5 | 2026-10-03 |
| 6 | S06 | competitor | obra/superpowers skills framework | R1 | 2026-10-03 |
| 7 | S07 | competitor | mattpocock/skills | R1/R4 | 2026-10-03 |
| 8 | S08 | competitor | affaan-m/ECC harness | R1 | 2026-10-03 |
| 9 | S09 | competitor | NousResearch/hermes-agent | R3 | 2026-10-03 |
| 10 | S10 | competitor | book-to-skill pipeline | P1 | 2026-10-03 |
| 11 | S11 | adjacent | anything-to-skill | P1 | 2026-10-03 |
| 12 | S12 | adjacent | Skill_Seekers export layouts | R5 | 2026-10-03 |
| 13 | S13 | adjacent | godot-agent triple delivery | R3/P5 | 2026-10-03 |
| 14 | S14 | adjacent | agentskills.io skill spec | R1 | 2026-10-03 |
| 15 | S15 | adjacent | MCP Python SDK (stdio) | P2 | 2026-10-03 |
| 16 | S16 | adjacent | Gutenberg catalog + ebooklib/pypdf/docx | P3 | 2026-10-03 |
| 17 | S17 | adjacent | Freud/James public-domain texts | P3 | 2026-10-03 |
| 18 | S18 | adjacent | open programming books list | P3 | 2026-10-03 |
| 19 | S19 | adjacent | Gumroad + itch.io seller pages | P5 | 2026-10-03 |
| 20 | S20 | adjacent | MoneyPrinterTurbo demo style | P5 | 2026-10-03 |

## S01-S05 status (the K-05 first-5, TRIAGE-2 verified 2026-10-03)

- S01-S05 Last read dated 2026-10-03 in `VISION.md` (Steal map).
- Cards filed + judged: `research/cards/2026-10-03-S01.md` (5 cards, C5 dupe
  folded into K-15), `-S02.md` (C4 fingerprint folds into K-20), `-S03.md`,
  `-S04.md`, `-S05.md` (checksum no-op folds into K-20, SKILL.md-presence stays).
  Merges recorded in `research/INDEX.md`; board rows K-15/K-19/K-20/K-17/K-18
  carry the landed proofs. TRIAGE-2 (planner-059) verified the dates + judged
  cards; the only missing piece was this hunt lane file.
- This file closes that piece: queries (Q1-Q12) + topics (1-8) + oldest-first
  order (S01-S20) above. K-05 is READY for lead verify + commit to DONE.
