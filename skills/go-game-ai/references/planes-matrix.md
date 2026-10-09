# Planes matrix: go-game-ai

Seven planes encode one 9x9 position. The call `encode_board` builds `board planes`, and `num_points` equals `board_width` times `board_height`. The call `encode_point` uses `row-major` order.

Pass rows, each checked in a `quick trial` on `9x9`:

- Plane 0 holds `own stones` and plane 1 holds `opp stones` for the two colors.
- The `liberty count` splits across `three planes`: one, two, three or more liberties.
- One plane marks the `ko point` so the bot skips the repeat.
- The last plane marks `to-play`: ones for Black, zeros for White.
- Size is `board_width` 9 by `board_height` 9, all `seven planes` stacked.

Provenance: `references/sources.md`.
