# MCTS matrix: go-game-ai

Tree search with random playouts, ideas only, no nets at runtime. Run with `stdlib only`.

Pass rows:

- Root is `MCTSNode` with `win_counts` and `num_rollouts` plus a `visit count` per child.
- Gate with `can_add_child`, then grow with `add_child` for legal points only.
- Rank children with `uct_score` and tune explore with `temperature`.
- Choose with `select_move` by `most visits` once simulations end.
- Close each sim with a `random playout` and score by `tromp-taylor` area count.
- State `no nets` in docs: planes plus tree, never a model file.

Provenance: `references/sources.md`.
