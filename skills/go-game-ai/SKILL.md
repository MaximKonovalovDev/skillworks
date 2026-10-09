---
name: go-game-ai
description: Use when coding a small Go board, planes encoding, or MCTS bot without neural nets at runtime.
version: 0.1.0
author: skillworks
tags: []
license: MIT
---

# go-game-ai

Small Go ideas in own words, no book text copied. Use `seven planes` of `board planes` plus MCTS with random playouts, and run with `stdlib only`. `no nets` at runtime: no Keras, no TensorFlow, no torch in the bot path. Start with the two matrices below, then read only the ONE `references/*.md` file that matches the task. Use when the task is a `9x9` board, a planes encoder, or a tree search move pick. The call `encode_board` turns one position into planes, and `num_points` counts board points. The call `encode_point` maps a point by `row-major` order to one index. The `quick trial` runs on 9x9 in under a second.

NOT for: training neural nets or tuning model weights (leave them to the ML skill that owns them).

## Planes matrix

Encode a 9x9 board as `seven planes` of `board planes`. The call `encode_board` turns one position into planes, and `num_points` counts `board_width` times `board_height`. The call `encode_point` maps a point by `row-major` order to one index.

- Keep `own stones` on plane 0 and `opp stones` on plane 1 for the two colors (`0045.txt`).
- Split the `liberty count` across `three planes`: one liberty, two liberties, three or more (`0067.txt`).
- Mark the `ko point` on its own plane so the bot never repeats it (`0068.txt`).
- Mark `to-play` on the last plane: all ones when Black moves, all zeros when White moves (`0067.txt`).
- Use `board_width` 9 and `board_height` 9 for the `quick trial` on a `9x9` board (`0003.txt`).

Details and pass rows: `references/planes-matrix.md`.

## MCTS matrix

Search with a tree, not with nets. The node `MCTSNode` holds `win_counts` and `num_rollouts`, plus a `visit count` per child. The score `uct_score` picks the next branch, and `temperature` tunes how much to explore.

- Grow the tree from `MCTSNode` with `win_counts` for wins, `num_rollouts` for visits, and a `visit count` per child (`0045.txt`).
- Check `can_add_child` before adding a move, and add with `add_child` only for legal points (`0046.txt`).
- Score each child with `uct_score` using parent rollouts, child rollouts, win rate, and `temperature` (`0047.txt`).
- Pick the move with `select_move` by `most visits` after the simulations finish (`0146.txt`).
- Finish each sim with a `random playout` to the end, then score with `tromp-taylor` area count (`0147.txt`).

Details and pass rows: `references/mcts-matrix.md`.

## No-nets rule

Keep the bot runnable with `stdlib only` and `no nets` at runtime.

- Import only stdlib plus numpy for planes: `stdlib only` means no Keras import in the move path (`0070.txt`).
- State `no nets` in the run doc: the bot plays from planes plus tree, never from a model file (`0110.txt`).
- Prove on a `9x9` `quick trial`: `encode_board` plus `select_move` picks a legal move in under a second (`0000.txt`).

Recall sheet: `references/cheatsheet.md`. Provenance: `references/sources.md`.
