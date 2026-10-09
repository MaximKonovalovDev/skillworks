---
name: game-patterns-free
description: Game patterns from MIT code: game loop, update method, object pool, component and 15 more. Use when writing game loops, pooling, events or state code. Source prose is NonCommercial CC BY-NC-ND, never sold, code only.
version: 0.1.0
author: skillworks
tags: []
license: CC-BY-NC-SA-3.0 (source; NonCommercial, never sold)
---

# game-patterns-free

Built from owned sources. Start with `patterns.md`, then read only the ONE `references/*.md` domain it points to that matches the task. Use when the trigger topic matches this skill description.
NOT for: topics outside this skill (leave them to the skill that owns them).
Routes - read only the sibling that matches the task:
- Index: see `patterns.md` for the 4-domain map and pattern pointers.
- Sequencing (game loop, update, double buffer): see `references/sequencing.md` only for frame tasks.
- Decoupling (component, command, observer, queue, singleton, locator): see `references/decoupling.md` only for decoupling tasks.
- Optimization (pool, flyweight, dirty flag, spatial, locality): see `references/optimization.md` only for perf tasks.
- Behavioral (bytecode, state, sandbox, type object, prototype): see `references/behavioral.md` only for behavior tasks.
- Terms: see `glossary.md`.
- Recall: see `cheatsheet.md`.
Verify refs with `scripts/check-refs.py` (exit 0 means pointers hold).
Compose with peers when the task spans skills:
- For the peer-owned step, call it via `Skill: peer-skill-name`.
- After this skill route, call the next skill via `Skill: peer-skill-name`.
Verify before acting: check the source before any regulated, filed, or paid step.
