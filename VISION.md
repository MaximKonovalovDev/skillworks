# VISION: skillworks (2026-10-02)

# skillworks — book-to-skill factory (vision seed, owner Maxim, 2026-10-02)

Book or manual IN (only books you own the rights to, your own Forge docs, or public-domain Gutenberg books), tested Agent Skill + MCP server OUT. One tested skill pack per week. Sell $10-50 per pack.

Parts: P1 pipeline (extract, split, index, build, audit, eval, refresh, export); P2 MCP server (skill_search over stdio); P3 seeds (skills/flax-forge-ops from own Forge docs + Gutenberg downloads, never commit books you do not own); P4 eval gate (source-derived Q&A pass rate, red blocks ship); P5 shop lanes (Gumroad/direct listings + demos).

Gaps: domain-expertise skills (skill markets are all dev wrappers); honest eval (diagnostic, not a model metric); store listings with live demos.

Steals (credited in THIRD_PARTY_NOTICES.md): book-to-skill, anything-to-skill, Skill_Seekers export layouts, godot-agent triple delivery (skill + CLI + MCP).

Proof: `python -m pytest tests/ -q` green + eval pass-rate gate + MCP handshake. Done = one tested pack per week in skills/<name>/ served by the MCP.

Guards: copyright first (fingerprint lock, rebuild only on change); secrets never committed; PUBLIC repo, no private automation in it.

The proof that this vision is met: `python -m pytest tests/ -q`.

This file is the ground the research loop reaches for. The current research
crew owns bounded sweeps; `node C:/Users/me/Desktop/center/vision-check.mjs
skillworks` FAILs until the Scorecard, Parts, gaps and Steal map below are filled
in and kept fresh. Filling them is the loop's first work.

## Scorecard: skillworks against the best (percent of our final bar)

How to read it: 100 means our own final bar for that row is met. Every other
column says how much of that same bar the competitor meets today, with a source.
Our own number rises only by a proof command. At least 5 rows and 3 real
competitors, plus how we cover each row and where we beat them.
Unknown cells stay UNKNOWN. Ratings need a fixed n/m, a named `rubric: ID`,
`source: artifact`, version and real date. Unknown criteria stay in the shared
denominator; a draft or document alone cannot prove a product outcome.

| Row (part of our bar) | skillworks | ClawHub | SkillsGate | Skrun / Evos | How we cover it and beat them |
|---|---|---|---|---|---|
| R1 book-to-skill in hours, with receipts | 50% (3/6 rubric: pipe-proven-6 source: research/cards/2026-10-03-P1.md 2026-10-03) | 0% (0/6 rubric: pipe-proven-6 source: research/cards/2026-10-03-S01.md 2026-10-03) | 0% (0/6 rubric: pipe-proven-6 source: research/cards/2026-10-03-S02.md 2026-10-03) | UNKNOWN | 8-stage CLI each with receipt.json + fingerprint refresh + eval gate 0.6; timed split/index on progit seeds; graded-audit steal next into audit.py (swept 2026-10-03) |
| R2 honest eval gate (Q&A pass rate blocks ship) | 25% (1/4 rubric: eval-gate-4 source: sprint/board.md 2026-10-02) | UNKNOWN | UNKNOWN | UNKNOWN | gate at 0.6 refuses export; per-skill QA sets next |
| R3 MCP delivery (skill_search over stdio) | 33% (1/3 rubric: mcp-serve-3 source: sprint/board.md 2026-10-02) | UNKNOWN | UNKNOWN | UNKNOWN | triple delivery: skill + CLI + MCP in one pack; handshake proof next |
| R4 domain packs beyond dev wrappers | 12% (1/8 rubric: domain-packs-8 source: sprint/board.md 2026-10-02) | UNKNOWN | UNKNOWN | UNKNOWN | 1 tested domain pack per week from owned books (psychology, programming first) |
| R5 export targets (claude, codex, opencode, gemini) | 0% (0/4 rubric: export-targets-4 source: sprint/board.md 2026-10-02) | UNKNOWN | UNKNOWN | UNKNOWN | one build, four copy-layout exports, tested per target next |
| R6 shop proof (sales, demos, price evidence) | 0% (0/3 rubric: shop-proof-3 source: sprint/board.md 2026-10-02) | UNKNOWN | UNKNOWN | UNKNOWN | Vol 0 free sample skill + GIF demo + listing per pack; sales counted, views are not |

## Plans: which plan serves which part of the vision

List the board and every active plan. Serves contains exact Scorecard row names
separated by semicolons, or `every row: reason` / `none: reason`.

| Plan | Serves (Scorecard rows) | Board prefixes and notes |
|---|---|---|
| `sprint/board.md` | every row: the executable work list | each goal needs a next task and proof |

## Research contract

Read the vision, board and prior findings before searching. Each research batch
compares competitor code, an adjacent implementation and an arXiv paper where
relevant. Read the implementation and tests, not only the abstract. Record source
revision, license, baseline, target, existing home, proof command, tradeoff and
stop rule. Unknown remains unknown. Merge duplicates into one experiment; promote
only after local measurement and independent review. No useful new evidence means
resume a pending experiment or record a dated rejection, not another catalog.

## Parts vs the best (research keeps this table true)

One row per part of the product. `Ours` stays UNKNOWN until its proof command
runs; old `est.` rows are explicitly unmeasured. Code is copied only under MIT,
Apache-2.0, BSD, zlib or CC0, license read live.

| Part | Ours (UNKNOWN = unmeasured) | Best at it (license) | They beat us on | Steal next | Proof that measures us | Swept |
|---|---|---|---|---|---|---|
| P1 pipeline extract-to-export | 8 stages run, split 13 chunks 0.053s + index 13 rec 0.163s, eval 12/12=1.0, audit 2825 tok (measured 2026-10-03) | anything-to-skill (Apache-2.0 live 2026-10-03) | graded audit: always-loaded/on-trigger/on-demand + routing + body budget 2000 (https://github.com/asale-ai/anything-to-skill/blob/main/src/audit.rs) | graded audit rules into book2skill/audit.py (Apache-2.0) | book PDF to exported skill, timed, receipted | 2026-10-03 |
| P2 MCP server skill_search | est. 25 | godot-agent triple delivery (MIT) | bundled server per skill | stdio search + handshake test | MCP handshake + query returns seed skill | seed 2026-10-02 |
| P3 seeds (own docs + Gutenberg) | est. 10 | Project Gutenberg (public domain) | 60k free books | gutenberg.org download lane + work/ quarantine | 2 test books downloaded, none committed | seed 2026-10-02 |
| P4 eval gate 0.6 | est. 30 | Evos eval suite (check license live) | full eval suite | source-derived QA sets per skill | export refused under 0.6, logged | seed 2026-10-02 |
| P5 shop lanes + demos | 0 | ClawHub market (terms live) | live buyers | free sample + GIF demo + listing template | sales count, not views | seed 2026-10-02 |

## Open gaps (research closes these; the lead writes the answer above)

- G1 Competitors: who are the 3-5 best at what this vision promises, and what
  does each do better today? Evidence: their own pages, releases and numbers.
- G2 The bar: what does "done" measure, in numbers, for each part?
- G3 The edge: where can we be the best, and why can the others not follow?

## Steal map (scouts: what we read, oldest first)

At least 10 competitors and 10 adjacent sources, each tied to a part; the steal
researcher reads the row read longest ago and writes its date back.

| ID | Kind | Sources | Part | Question | License (read live) | Last read |
|---|---|---|---|---|---|---|
| S01 | competitor | ClawHub skill market | R4/P5 | what sells, what format wins? | terms live (proprietary registry, 2026-10-03) | 2026-10-03 |
| S02 | competitor | SkillsGate index (45k skills) | R4 | where is the domain gap? | MIT repo + site terms live (2026-10-03) | 2026-10-03 |
| S03 | competitor | Skrun skill-as-API | R3 | API vs MCP serving? | MIT (ideas-only, live 2026-10-03) | 2026-10-03 |
| S04 | competitor | Evos domain skills + eval suite | R2/R4 | how is their eval built? | check live | never |
| S05 | competitor | agentic-prompt-sync | R5 | AGENTS.md sync across targets? | MIT | never |
| S06 | competitor | obra/superpowers skills framework | R1 | skill layout that agents love? | MIT | never |
| S07 | competitor | mattpocock/skills | R1/R4 | real-engineer skill shape? | MIT | never |
| S08 | competitor | affaan-m/ECC harness | R1 | instincts/memory for skill use? | MIT | never |
| S09 | competitor | NousResearch/hermes-agent | R3 | agent loop calling skills? | MIT | never |
| S10 | competitor | book-to-skill pipeline | P1 | chunk + index design? | MIT | never |
| S11 | adjacent | anything-to-skill | P1 | refresh lock + audit? | MIT | never |
| S12 | adjacent | Skill_Seekers export layouts | R5 | per-target copy layout? | check live | never |
| S13 | adjacent | godot-agent triple delivery | R3/P5 | skill+CLI+MCP bundle? | MIT | never |
| S14 | adjacent | agentskills.io skill spec | R1 | SKILL.md frontmatter rules? | spec (no code) | never |
| S15 | adjacent | MCP Python SDK (stdio) | P2 | handshake + tool schema? | Apache-2.0 | never |
| S16 | adjacent | Gutenberg catalog + ebooklib/pypdf/docx | P3 | clean text extract? | PD / MIT / Apache | never |
| S17 | adjacent | Freud/James public-domain texts | P3 | first psychology test books? | public domain | never |
| S18 | adjacent | open programming books (free-programming-books list) | P3 | first programming test books? | CC/MIT mix, check each | never |
| S19 | adjacent | Gumroad + itch.io seller pages | P5 | price + listing shape? | terms live | never |
| S20 | adjacent | MoneyPrinterTurbo demo style | P5 | GIF demo that sells? | check live | never |

## Delivery evidence (the 10x product bar)

A pack ships only with: stranger-15min proof (a stranger installs and uses it in 15 min) | eyes-vs-reference (side-by-side with the ClawHub twin) | dogfood (our forge loop uses the skill for real work) | sellers' own pages linked as price evidence | GIF-first demo | Vol 0 free sample skill | bundle after 3 (bundle only after 3 sold Vols) | UNKNOWN views = FAIL (views without sales = FAIL) | PREP-ONLY is not shipped (a listing draft with no proof = not shipped). Views and drafts are not sales.

Card (every steal): Source (repo@sha `path:line` or URL) and license | What it
does | Home (an existing file here; no home = reject) | Fixes (the part) | Net
lines | Proof (no proof = reject) | Effort S/M/L and risk. The research merge
seat judges every card and keeps the rejects.
