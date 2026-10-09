---
name: handsrust-code
description: Use when coding Flappy state machines, seeded drunkard dungeons, or intent movement with collisions in Rust game code without external crates.
version: 0.1.0
author: skillworks
license: MIT
---

# Hands-on Rust code patterns

Rules distilled from Wolverson Hands-on Rust 2021 for dependency-free game logic: Flappy state machines, seeded drunkard dungeons, and intent movement with collisions. Each rule names the exact type or function and the cargo proof. Detail lives in `references/pairs.md` (machine list `references/pairs.json`), replayed by `scripts/handsrust_code.py`. Every fixture is dependency-free with no bracket-lib and no legion, and runs with real cargo 1.97.1 offline with `CARGO_NET_OFFLINE=1` in a fresh scratch dir under `$TEMP/opencode`.

## Flappy states go Menu to Playing to End

- `GameMode` has `Menu`, `Playing`, and `End`, and `State::new()` starts in `Menu` [src: references/pairs.md#hr-p01]
- `State::restart()` moves `Menu` to `Playing` and also moves `End` back to `Playing` [src: references/pairs.md#hr-p01]
- `State::play()` moves `Playing` to `End` and leaves `Menu` alone [src: references/pairs.md#hr-p01]
- `cargo test` on `state_demo` prints `test result: ok` with `3 passed` and exit 0 [src: references/pairs.md#hr-p01]

## Seeded drunkard keeps every floor connected

- `Rng` is a seeded small LCG, and `range(lo, hi)` returns inside `[lo, hi)` [src: references/pairs.md#hr-p02]
- `STAGGER_DISTANCE` is `400` steps of drunkard walk from the center on a `20x20` map [src: references/pairs.md#hr-p02]
- `build_map(seed)` is deterministic: the same seed gives the same map, and `1` and `2` give different maps [src: references/pairs.md#hr-p02]
- `floor_connected` runs BFS over floor cells, the offline stand-in for the Dijkstra prune that keeps connectivity, like the seeded `RandomNumberGenerator` in the book [src: references/pairs.md#hr-p02]
- `cargo test` on `drunk_demo` prints `test result: ok` with `3 passed` and exit 0 [src: references/pairs.md#hr-p02]

## Intent moves only through open tiles

- `WantsToMove` carries `dx` and `dy` as the move intent [src: references/pairs.md#hr-p03]
- `Map::can_enter` is the gate: borders and out-of-bounds tiles return false [src: references/pairs.md#hr-p03]
- `apply_intent` applies a `WantsToMove` only when `can_enter` allows the next `Point` [src: references/pairs.md#hr-p03]
- `collisions` calls `retain` to remove the enemy on the player pos and keep the rest [src: references/pairs.md#hr-p03]
- `cargo test` on `intent_demo` prints `test result: ok` with `3 passed` and exit 0 [src: references/pairs.md#hr-p03]
