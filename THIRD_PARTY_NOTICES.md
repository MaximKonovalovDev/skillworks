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
* anthropics/skills + agentskills.io specification — SKILL.md frontmatter
  fields and progressive-disclosure layout (spec-defined, free to implement).
* Unity-Technologies/skills, gamedev-skills/awesome-gamedev-agent-skills
  (Apache-2.0), majidmanzarpour/threejs-game-skills (MIT), aigengame/godot-agent
  (MIT) — skill-pack and router patterns; CLI+bundled-skill+MCP triple
  delivery shape from godot-agent.
