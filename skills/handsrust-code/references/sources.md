# Sources and licences (read 2026-10-09)

The skill text and every example are written fresh. The book files
below were read to check each rule. Only short names and output
fragments are quoted, each with its file.

- Wolverson H. - Hands-on Rust - 2021 (Herbert Wolverson, Pragmatic Bookshelf). Upstream https://pragprog.com/titles/hwrust/hands-on-rust/, verified live 2026-10-09.
  - Licence: this skill is original work under MIT. The book text is not copied; all Rust code is written from scratch (logic only, minimal). Short quotes only: type names and one-line outputs.
  - Local code read from `work/inbox-books/Wolverson H. - Hands-on Rust - 2021/code` (git-ignored, never committed). Files read:
    - `FirstGameFlappyAscii/flappy_states/src/main.rs` (GameMode Menu Playing End, restart Menu to Playing, play Playing to End)
    - `MoreInterestingDungeons/drunkard/src/map_builder/drunkard.rs` (DrunkardsWalkArchitect, STAGGER_DISTANCE 400, seeded RandomNumberGenerator, Dijkstra prune keeps connectivity)
    - `EntitiesComponentsAndSystems/dungeonecs` plus `TurnBasedGames/intent` (WantsToMove intent, movement can_enter_tile gate, collisions remove enemy on player pos)
  - Compiler outputs quoted in pairs.md were measured on this PC with cargo 1.97.1 and rustc 1.97.1 on 2026-10-09, not copied from the book.
- The trial sheet `evals/handsrust-code_trials.jsonl` (4 tasks) pins each task to its code path above.
- This skill is original work under MIT. It is free to use and share.

Credit line for THIRD_PARTY_NOTICES.md: handsrust-code (MIT original skill, logic only from Wolverson Hands-on Rust 2021 read 2026-10-09; own words and own examples, short quotes only).
