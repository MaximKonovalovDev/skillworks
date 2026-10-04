# VISION tables: skillworks (moved out of VISION.md 2026-10-03)

The research tables of `VISION.md`. The planner and the lead edit them here (the vision researcher seat retired 2026-10-04; the toolsmith updates a Parts row when its tool lands); `VISION.md` stays the short top every agent re-reads. `node C:/Users/me/Desktop/center/vision-check.mjs skillworks` reads both files as one text.

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
| R1 book-to-skill in hours, with receipts | 50% (3/6 rubric: pipe-proven-6 2026-10-03 source: research/cards/2026-10-04-P1.md) | 0% (0/6 rubric: pipe-proven-6 source: research/cards/2026-10-03-S01.md 2026-10-03) | 0% (0/6 rubric: pipe-proven-6 source: research/cards/2026-10-03-S02.md 2026-10-03) | 0% (0/6 rubric: pipe-proven-6 source: research/cards/2026-10-03-S06-S10.md 2026-10-03) | one-command make (extract/split/index/build/eval/audit/+export) each with receipt + fingerprint refresh + eval gate 0.6; split 13 chunks + index 13 rec, eval 12/12=1.0, audit 8 files/3554 tok canonical (export skipped) on progit, pytest 151 passed 27 skipped; graded-audit steal next into audit.py (swept 2026-10-03) |
| R2 honest eval gate (Q&A pass rate blocks ship) | 50% (2/4 rubric: eval-gate-4 source: research/cards/2026-10-03-P4.md 2026-10-03) | 0% (0/4 rubric: eval-gate-4 source: research/cards/2026-10-03-S06-S10.md 2026-10-03) | 0% (0/4 rubric: eval-gate-4 source: research/cards/2026-10-03-S06-S10.md 2026-10-03) | 75% (3/4 rubric: eval-gate-4 source: research/cards/2026-10-03-P4.md 2026-10-03) | offline substring gate 0.6 refuses export below gate proven (progit 1.0 + freud 0.833 + james 0.667 ship, sub-gate scratch refused) + per-skill QA + eval_report.json; registry + failure_score steal next into eval.py (swept 2026-10-03) |
| R3 MCP delivery (skill_search over stdio) | 33% (1/3 rubric: mcp-serve-3 source: research/cards/2026-10-03-P2.md 2026-10-03) | 0% (0/3 rubric: mcp-serve-3 source: research/cards/2026-10-03-S01.md 2026-10-03) | 0% (0/3 rubric: mcp-serve-3 source: research/cards/2026-10-03-S02.md 2026-10-03) | 0% (0/3 rubric: mcp-serve-3 source: research/cards/2026-10-03-S03.md 2026-10-03) | stdio skill_search over 3 seed skills re-proven today (handshake + list + call returns progit-branching x2 score 41 top 41, pytest 12 passed); ClawHub is registry/CLI with no stdio serve, SkillsGate is desktop Discover with no stdio serve, Skrun is HTTP POST /run consuming MCP inside with no stdio skill_search; signature-derived inputSchema + CacheHint steal next from FastMCP (Apache-2.0) + godot (MIT) into mcp_server/server.py (swept 2026-10-03) |
| R4 domain packs beyond dev wrappers | 25% (2/8 rubric: domain-packs-8 source: research/cards/2026-10-03-P3.md 2026-10-03) | 0% (0/8 rubric: domain-packs-8 source: research/cards/2026-10-03-S06-S10.md 2026-10-03) | 0% (0/8 rubric: domain-packs-8 source: research/cards/2026-10-03-S06-S10.md 2026-10-03) | 75% (6/8 rubric: domain-packs-8 source: research/cards/2026-10-03-S06-S10.md 2026-10-03) | 3 skills built (freud 0.833 + james 0.667 ship, progit 1.0), work/ quarantined, PD supply 79,523 eBooks live; header/footer marker strip (MIT riser) + layout-mode + body-only + license-allowlist steal next into extract (swept 2026-10-03) |
| R5 export targets (claude, codex, opencode, gemini) | 0% (0/4 rubric: export-targets-4 source: sprint/board.md 2026-10-02) | 25% (1/4 rubric: export-targets-4 source: research/cards/2026-10-03-S06-S10.md 2026-10-03) | 25% (1/4 rubric: export-targets-4 source: research/cards/2026-10-03-S06-S10.md 2026-10-03) | 0% (0/4 rubric: export-targets-4 source: research/cards/2026-10-03-S06-S10.md 2026-10-03) | one build, four copy-layout exports, tested per target next |
| R6 shop proof (sales, demos, price evidence) | 0% (0/3 rubric: shop-proof-3 source: research/cards/2026-10-03-P5.md 2026-10-03) | 67% (2/3 rubric: shop-proof-3 source: research/cards/2026-10-03-P5.md 2026-10-03) | 33% (1/3 rubric: shop-proof-3 source: research/cards/2026-10-03-S02.md 2026-10-03) | 0% (0/3 rubric: shop-proof-3 source: research/cards/2026-10-03-S06-S10.md 2026-10-03) | export claude dir copy today; ZIP artifact + Vol 0 sample + GIF-first demo + listing template with honest 0-sales counter steal next into export.py/listing (swept 2026-10-03) |

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
| P1 pipeline extract-to-export | one-command make (extract/split/index/build/eval/audit/+export), split 13 chunks + index 13 rec, eval 12/12=1.0 (evals/progit-branching_qa.jsonl), audit 3554 tok over 8 files canonical (export skipped), pytest 151 passed 27 skipped (measured 2026-10-03 source: research/cards/2026-10-04-P1.md) | anything-to-skill (Apache-2.0 live 2026-10-03) + superpowers (MIT live 2026-10-03) + ddeleon82/anything-to-skill pipeline (MIT live 2026-10-03) | graded audit: always-loaded/on-trigger/on-demand + routing + body budget 2000 (https://github.com/asale-ai/anything-to-skill/blob/main/src/audit.rs) | graded audit rules into book2skill/audit.py (Apache-2.0) | book PDF to exported skill, timed, receipted | 2026-10-03 |
| P2 MCP server skill_search | 78-line stdio server, initialize+tools/list+tools/call OK, query 'branching git' returns progit-branching x2 score 41, pytest 12 passed (re-measured 2026-10-03 source: research/cards/2026-10-03-P2.md) | godot-agent triple delivery (MIT live 2026-10-03) + hermes-agent skills_list/skill_view (MIT live 2026-10-03) + MCP python-sdk stdio (MIT live 2026-10-03) + FastMCP decorator auto-schema (Apache-2.0 live 2026-10-03) | decorator-derived inputSchema + tools/list CacheHint 1h (https://github.com/PrefectHQ/fastmcp + https://github.com/aigengame/godot-agent/blob/main/src/gda/mcp/server.py) + generated per-command tools + envelope + list/view split with collision refusal + traversal reject + fd 0/1 claim + divert/restore vs our single untyped skill_search, tools/list with no inputSchema, no view, no claim | signature-derived inputSchema + CacheHint into mcp_server/server.py (Apache-2.0 + MIT) | MCP handshake + query returns seed skill | 2026-10-03 |
| P3 seeds (own docs + Gutenberg) | work/freud-dreams 1273085 B file (1241682 chars, Gutenberg header+footer still present) + work/progit 63854 B file (62576 chars clean), skills freud 10/12=0.833 ships + progit 12/12=1.0, work/ gitignored + pytest 12 passed (measured 2026-10-03 source: research/cards/2026-10-03-P3.md; eval re-measured 2026-10-04 live eval_report.json) | Project Gutenberg (public domain live 2026-10-03) + aerkalov/ebooklib (AGPL-3.0 ideas-only live 2026-10-03) + py-pdf/pypdf (BSD live 2026-10-03) + EbookFoundation/free-programming-books (CC-BY-4.0 live 2026-10-03) + kiasar/gutenberg_cleaner riser (MIT live 2026-10-03) | body-only + pagebreak labels (https://github.com/aerkalov/ebooklib/blob/master/ebooklib/utils.py) + layout-mode tables/code order (https://github.com/py-pdf/pypdf/blob/main/pypdf/_page.py) + license-filtered list (https://github.com/EbookFoundation/free-programming-books) + header/footer marker strip (https://github.com/kiasar/gutenberg_cleaner/blob/master/_cleaning_options/strip_headers.py) vs our plain extract with unstripped PG header; 79,523 PD eBooks (https://www.gutenberg.org/) | Gutenberg header/footer marker strip into book2skill/extract.py (MIT) | 2 test books downloaded, none committed, 2 seed skills built | 2026-10-03 |
| P4 eval gate 0.6 | 57-line eval.py + 67-line export.py GATE 0.6, progit 12/12=1.0 ships + freud 10/12=0.833 ships, pytest 12 passed (measured 2026-10-03; eval re-measured 2026-10-04 live eval_report.json) | ai-evos/agent-skills (Apache-2.0 live 2026-10-03) + stanfordnlp/dspy (MIT live 2026-10-03) + EleutherAI/lm-evaluation-harness (MIT live 2026-10-03) | weighted pass/partial/fail 0.7 + baseline lift +11.8pp + metric registry with mean/stderr (https://github.com/ai-evos/agent-skills/blob/main/shared/eval_framework.py + https://github.com/stanfordnlp/dspy/blob/main/dspy/evaluate/evaluate.py + https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/api/metrics.py) | metric registry + EvaluationResult/failure_score into book2skill/eval.py (MIT) + trial runner tools/skill_trial.py stranger with/wo grade into trial-proof.json (TS-3 landed 2026-10-04; pipe-run 12 runs with 1.0 lift 0.8333) | export refused under 0.6, logged | 2026-10-03 |
| P5 shop lanes + demos | export claude dir only (1 target, 11 files, no ZIP/lock), no listing.md, no demo GIF, 0 sales, pytest 12 passed (measured 2026-10-03) | ClawHub registry (proprietary live 2026-10-03) + Skill_Seekers (MIT live 2026-10-03) + godot-agent (MIT live 2026-10-03) + MoneyPrinterTurbo (MIT live 2026-10-03) | versioned bundles + semver/tags/changelog + downloads/stars/scan + public inspect pages (https://docs.openclaw.ai/clawhub) + ZIP_DEFLATED SKILL.md+refs/scripts/assets (https://github.com/yusufkaraaslan/Skill_Seekers/blob/development/src/skill_seekers/cli/adaptors/claude.py) + triple bundle + demos gallery (https://github.com/aigengame/godot-agent) + 16-work video-first demo (https://github.com/harry0703/MoneyPrinterTurbo) vs our 1 dir copy, no artifact/demo/listing | Claude ZIP artifact into book2skill/export.py (MIT) | export progit-branching claude ZIP with SKILL.md at root, timed, receipted | 2026-10-03 |

## Open gaps (research closes these; the lead writes the answer above)

G1 answered (2026-10-04, planner adopts research/cards/2026-10-03-G1.md): obra/superpowers (MIT, ★294868) owns skill shape/TDD-for-skills; ClawHub (proprietary registry, docs.openclaw.ai/clawhub) owns versioned bundles + scans + lock; ai-evos/agent-skills (Apache-2.0) owns model-graded skill-vs-zero-primed-baseline eval; SkillsGate+skills.sh (MIT, ★1342) owns preview-then-install discovery (dev-only: our domain-pack edge); asale-ai/anything-to-skill (Apache-2.0) owns model-free graded audit | sources: https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md https://docs.openclaw.ai/clawhub https://github.com/ai-evos/agent-skills/blob/main/shared/eval_framework.py https://github.com/skillsgate/skillsgate https://github.com/asale-ai/anything-to-skill full map: research/cards/2026-10-03-G1.md

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
| S04 | competitor | Evos domain skills + eval suite | R2/R4 | how is their eval built? | Apache-2.0 (live 2026-10-03) | 2026-10-03 |
| S05 | competitor | westonplatter/aps (agentic-prompt-sync) | R5 | AGENTS.md sync across targets? | BSD-3-Clause (live 2026-10-03) | 2026-10-03 |
| S06 | competitor | obra/superpowers skills framework | R1 | skill layout that agents love? | MIT (live 2026-10-03) | 2026-10-03 |
| S07 | competitor | mattpocock/skills | R1/R4 | real-engineer skill shape? | MIT (live 2026-10-03) | 2026-10-03 |
| S08 | competitor | affaan-m/ECC harness | R1 | instincts/memory for skill use? | MIT (live 2026-10-03) | 2026-10-03 |
| S09 | competitor | NousResearch/hermes-agent | R3 | agent loop calling skills? | MIT (live 2026-10-03) | 2026-10-03 |
| S10 | competitor | book-to-skill pipeline | P1 | chunk + index design? | MIT (live 2026-10-03) | 2026-10-03 |
| S11 | adjacent | anything-to-skill (asale-ai/anything-to-skill) | P1 | refresh lock + audit? | Apache-2.0 (live 2026-10-03) | 2026-10-03 |
| S12 | adjacent | Skill_Seekers export layouts | R5 | per-target copy layout? | MIT (ideas-only, live 2026-10-03) | 2026-10-03 |
| S13 | adjacent | godot-agent triple delivery | R3/P5 | skill+CLI+MCP bundle? | MIT (live 2026-10-03) | 2026-10-03 |
| S14 | adjacent | agentskills.io skill spec | R1 | SKILL.md frontmatter rules? | spec reference-only live 2026-10-03 | 2026-10-03 |
| S15 | adjacent | MCP Python SDK (stdio) | P2 | handshake + tool schema? | MIT (live 2026-10-03) | 2026-10-03 |
| S16 | adjacent | Gutenberg catalog + ebooklib/pypdf/docx | P3 | clean text extract? | AGPL-3.0 (ebooklib LICENSE.txt live 2026-10-03) / PD / BSD / MIT | 2026-10-03 |
| S17 | adjacent | Freud/James public-domain texts | P3 | first psychology test books? | public domain | 2026-10-03 |
| S18 | adjacent | open programming books (free-programming-books list) | P3 | first programming test books? | CC/MIT mix, check each | 2026-10-03 |
| S19 | adjacent | Gumroad + itch.io seller pages | P5 | price + listing shape? | terms live | 2026-10-03 |
| S20 | adjacent | MoneyPrinterTurbo demo style | P5 | GIF demo that sells? | MIT (live 2026-10-03) | 2026-10-03 |

