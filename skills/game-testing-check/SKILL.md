---
name: game-testing-check
description: Checklists for game playtests and performance runs distilled from a modern game QA manual. Use when planning a playtest, a stress run, or a perf pass before a build ships.
version: 0.1.0
author: skillworks
tags: []
license: MIT
---

# game-testing-check

Playtest and performance checklists in own words. No book text is copied. Start with the two matrices below, then read only the ONE `references/*.md` file that matches the task. Use when the task is a playtest plan, a stress or load check, or a perf pass on frame rate and lag.

NOT for: code patterns or netcode flags (leave them to the skill that owns them).

## Playtest matrix

Run three formats. A `one-on-one` pairs one player with one moderator. A `focus group` holds 5 to 10 testers in one room. An `extended playtest` asks the player to play for several days.

- The `moderator` guides the player, asks questions, and `takes notes`. Recording is on. The moderator is often a `UX designer` or someone close to the design.
- Play as the player, not as QA: put on the `player shoes` and judge as a user would.
- Recruit the right `target audience`. Use `screening surveys` to find them. Players are `not biased` toward the company or the game.
- The build must be mature: a `smooth experience` that is `bug-free` enough to judge fun, not bugs.
- Cover the `tutorial` first: can a new player understand it with no help.
- Judge the `fun factor` in plain words. Judge `difficulty balancing` across levels: too easy, too hard, or fair.

Details and pass rows: `references/playtest-matrix.md`.

## Perf matrix

Check how the game holds up under pressure. `stress testing` simulates pressure such as `multiple players` joining at once or a rapid rise in downloads. `load testing` needs some coding work and it can be `automated`. Both are often run by `backend developers` with QA.

- Ask `performance under stress`: what is the `frame rate`, is there `lag` or delay.
- Check `compatibility` on each target device and OS. Check `installability`: size, update path, clean removal, file location.
- Build `test sets` for devices: cover low, mid, and high tiers. This is `hardware compatibility`.
- Watch `scalability`: can the game take new content and new features.

Details and pass rows: `references/perf-matrix.md`.

## Test basics

Light process that keeps the matrices honest.

- Write small cases, or use a `test charter` for `exploratory testing` when docs would slow the team.
- Pair up for ideas: `pairwise testing` means two testers of different seniority run together, one lead and one follower. Two heads are better than one: the pair finds more than either alone. The phrase to remember is `two heads`.
- Plan by risk: `risk identification` lists what can break, `risk analysis` weighs impact on player, game, and company.
- Gate the build with `smoke testing` on basic function with a time benchmark. Invite real players with `beta testing`. Allow skilled testers an `ad hoc` pass with no script after formal tests.
- Track each bug with a `repro rate` such as 10/10 and a clear `bug flow` from found to fixed to verified.

Recall sheet: `references/cheatsheet.md`. Provenance: `references/sources.md`.

