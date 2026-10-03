# VISION.md intro before 2026-10-03 (moved, text unchanged)

The text that stood above the first `## ` heading of VISION.md until the 2026-10-03 fixer pass.

---

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

