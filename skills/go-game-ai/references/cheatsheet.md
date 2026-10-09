# Cheatsheet: go-game-ai

Planes: `seven planes` of `board planes`. Call `encode_board`, count with `num_points`, map with `encode_point` by `row-major`. Keep `own stones` and `opp stones`. Split `liberty count` over `three planes`. Mark `ko point` and `to-play`. Size `board_width` 9, `board_height` 9, board `9x9`, run the `quick trial`.

MCTS: node `MCTSNode` holds `win_counts` and `num_rollouts` with a `visit count`. Gate `can_add_child`, grow `add_child`. Score `uct_score` with `temperature`. Pick with `select_move` by `most visits`. End with `random playout`, score `tromp-taylor`.

Runtime: `stdlib only` and `no nets` at runtime, never a model file.
