---
role: builder
title: K-18 publish-ready frontmatter (version/author/tags)
chain: start
---

Goal: K-18 DONE (R5): book2skill/build.py writes version (0.1.0 default) + author + tags via _frontmatter (name+description stay first). Baseline build.py has name+description only (plus K-36 NAME_RULE — keep it intact).
Scope: book2skill/build.py (_frontmatter only) + ONE test (rebuilt seed frontmatter carries version/author/tags, name+description first). No other files.
Proof: rebuilt seed SKILL.md frontmatter versioned + `python -m pytest tests/ -q` green (expect 27 passed: 26 + 1 new; parallel lane may move baseline — report actual).
Stop: S/M 30 min. End with the RESULT line.
Record: K-18 [S01-C4] | versioned frontmatter + test, pytest green
Board: sprint/board.md K-18 READY -> DONE needs judge PASS + commit by lead.
