# Third-party notices — ideas and formats combined here

Pipeline design combines patterns from these repos. Only ideas and
spec-defined formats are reused; no code is copied. Check each license
before vendoring anything.

* virgiliojr94/book-to-skill (MIT) — SKILL.md + chapters + glossary +
  patterns + cheatsheet output shape; multi-parser extraction.
* asale-ai/anything-to-skill (Apache-2.0) — two-pass notes-then-skill build,
  token-cost audit, eval pass rate, fingerprint refresh lock.
* zhimaAi/BookToSkill (Apache-2.0) — 5k-char split, grounded JSONL index,
  strict validation, deterministic merge.
* T-Zevin/pdf-to-skill (no license, all rights reserved) — transfer-map idea
  only; no code taken.
* yusufkaraaslan/Skill_Seekers (MIT) — multi-target export, quality/sync/scan
  command shape.
* obra/superpowers (MIT) — progressive-disclosure SKILL.md + references/
  skill-pack layout (T-01); no code copied.
* mozilla/pdf.js (Apache-2.0) — per-page getTextContent ordering idea for the
  extract stage (T-02); implemented against pypdf, no code copied.
* python-openxml/python-docx (MIT) — paragraph/table document walk for the
  docx lane (T-03); uses the library, pattern only.
* simonw/llm (Apache-2.0) — versioned prompt-fragment files instead of inline
  strings (T-04); `prompts/build-skill.md` carries the version stamp.
* stanfordnlp/dspy (MIT) — signature-compiled QA contract for growing
  source-derived eval sets (T-05); `eval.grow_qa` reimplements the idea.
* kiasar/gutenberg_cleaner (MIT) — Gutenberg header/footer TEXT_START/END marker-strip idea reimplemented in extract (K-28); no code copied.
* anthropics/skills skill-creator scripts/quick_validate.py + package_skill.py (licence: none declared, read live 2026-10-04 via gh api repos/anthropics/skills, pinned commit 8a1541c) - validate-then-package shape for the distill check gate (frontmatter, kebab name, description budget) and the plan-then-check order; ideas only, no code copied.
* ai-evos/agent-skills `shared/eval_framework.py` (Apache-2.0 repo spdx read live 2026-10-04 via gh api repos/ai-evos/agent-skills, pinned commit 1eda1fe, file blob cdc34c8) + anthropics/skills `skills/skill-creator/scripts/aggregate_benchmark.py` (Apache-2.0 LICENSE.txt in its folder read live 2026-10-04, pinned commit 8a1541c, file blob 3e66e8c1; repo-level licence none declared) — with-skill versus bare-baseline runs with lift between them, and with_skill/without_skill run layouts aggregated into one summary, behind `tools/skill_trial.py` sheet+grade (TS-3); ideas only, no code copied.
* asale-ai/anything-to-skill src/audit.rs (Apache-2.0, read live 2026-10-04 via gh api repos/asale-ai/anything-to-skill, pinned commit f03d157) - graded-audit idea behind the distill check locator and pairs counts next to the token budgets; ideas only, no code copied.
* microsoft/markitdown (MIT, licence spdx read live 2026-10-04 via gh api repos/microsoft/markitdown, pinned main 7ccc027) - EPUB/PDF/DOCX converters (packages/markitdown/src/markitdown/converters/_epub_converter.py, _pdf_converter.py) behind `book2skill extract --engine markitdown` (TS-4); library used from .tools/py, no code copied.
* jsvine/pdfplumber (MIT, licence spdx read live 2026-10-04 via gh api repos/jsvine/pdfplumber, pinned stable 4c64b92) - lattice table recovery and Courier-font code fencing on the markitdown PDF path plus the pypdf-empty fallback in the classic PDF path (TS-4); library used, no code copied.
* Unity-Technologies/skills, gamedev-skills/awesome-gamedev-agent-skills
  (Apache-2.0), majidmanzarpour/threejs-game-skills (MIT), aigengame/godot-agent
  (MIT) — skill-pack and router patterns; CLI+bundled-skill+MCP triple
  delivery shape from godot-agent.
* MicrosoftDocs/PowerShell-Docs (CC-BY-4.0 documentation text, MIT code samples, read live 2026-10-03, re-read 2026-10-04, commit a3de8f2) - the checked source for skills/pwsh-for-bash-writers: quoting, redirection, exit-code and pipeline-chain rules, rewritten in our own words and tested. Changes: rewritten, shortened, every example run.
* progit/progit2, Pro Git by Scott Chacon and Ben Straub (CC BY-NC-SA 3.0, read live 2026-10-03) - the source for skills/git-one-branch next to skills/progit-branching. The skill text is a derived work under the same licence: attribution, NonCommercial, ShareAlike. It is shared free and never sold.
* microsoft/playwright docs (Apache-2.0, read live 2026-10-03, re-read 2026-10-04, tag v1.63.0 commit 1b025d7) - ideas only (auto-waiting, locators first, context isolation, request routing, channel msedge) for skills/real-browser-automation; no text or code copied.
* ChromeDevTools/devtools-protocol (BSD-3-Clause, read live 2026-10-03, re-read 2026-10-04, commit d209a9a) - every CDP method, event and parameter name in skills/real-browser-automation checked against json/browser_protocol.json and json/js_protocol.json; no text copied.
* bevyengine/bevy (MIT OR Apache-2.0) and bevyengine/bevy-website (MIT) - Bevy 0.19.1 API names, file and line evidence, and 0.18-to-0.19 migration facts for skills/bevy-rust-ecs; own words and own code, no code copied; pinned tag v0.19.1, commit b56fc29d3016e641754765244b5ba3f9cc504671, re-read 2026-10-04.
* cchao123/skills-manager (MIT, licence spdx read live 2026-10-04 via gh api, pinned f5ab5fb) - marketplace listing fields (author, repository, stars, weekly-installs) behind the listing shape in tools/pack_check.py FIELDS (TS-5); ideas only, no code copied.
* openclaw/clawhub (MIT, licence spdx read live 2026-10-04 via gh api, pinned 00f356544bd4624542cf10b69b5f8097fe397b7a) - publish-readiness gate (SKILL.md, semver version, description, files manifest with path+size+sha256, bundle-size cap, junk-file filter) in convex/lib/skillPublish.ts behind the buyer-zip manifest checks in tools/pack_check.py (TS-5); ideas only, no code copied.
* autonomous-factory engine/publish_preflight.py audit() (own fleet, via arsenal --list) - buyer-file gate called read-only from tools/pack_check.py on a staged factory-layout copy (TS-5); no code copied, no vendoring.
* engine-builder (MIT skill text and scripts; Apache-2.0 docs read live 2026-10-04, ideas only, no text copied) - the land-or-claim builder skill in skills/engine-builder (DR-1004-1): lane creation, present-work verification, audit fix, queue retry, sub-slice landing; own words and own pairs, tested live.
