# Patterns: rust-wasm-game

Own-words detail for each SKILL.md rule. Terms only; no book prose is copied.

## Boot

The `#[wasm_bindgen(start)]` function is the module entry; it runs on page load. It logs readiness with `console::log_1(&JsValue::from_str("loaded"))`. It calls `console_error_panic_hook::set_once()` once so panics print with context. Asset loading runs in a `browser::spawn_local` async block, and the game object is built after the block resolves.

## Canvas

The canvas comes from `get_element_by_id("canvas")`, cast to `HtmlCanvasElement`. Its drawing handle is a `CanvasRenderingContext2d`, wrapped in a `Renderer` struct. Game code calls `Renderer` methods only, so the raw context stays in one place.

## Sprite sheets

The atlas file maps to `Sheet` holding a map of `Cell` entries, both derived with `serde`. Each cell carries `spriteSourceSize`, the trimmed frame box without padding. One shared sheet plus one image serve every sprite; handles clone cheaply through `Rc`.

## Async loading

Each bitmap starts as `HtmlImageElement::new()` with `set_src` pointed at the file. Atlas JSON arrives through `fetch`, wrapped with `JsFuture::from` and awaited. The onload hook is a one-shot closure passed via `unchecked_ref` and pinned with `forget()` until it fires.

## Frame loop

The loop callback has type `LoopClosure`, a `Closure` over `FnMut(f64)`. The live instance sits in a `SharedLoopClosure`, shared through `Rc` with interior mutability. Each tick ends by calling `request_animation_frame` with the same closure, chaining frames forever.

## Game trait and timestep

Each screen implements `trait Game` with `initialize`, `update`, and `draw`. Logic advances in fixed steps of `FRAME_SIZE`, one sixtieth of a second in milliseconds. Real elapsed time gathers in `accumulated_delta`; the loop runs `update` while the debt exceeds the tick, then draws once.

## Keyboard input

The window listens for `keydown` and `keyup`, each yielding a `KeyboardEvent`. Events reduce into `KeyState`, whose `pressed_keys` map links each code to its event. Game code polls `contains_key(code)`; handlers insert on down and remove on up.

## Animation states

All poses live in the `RedHatBoyStateMachine` enum, from idle through running, sliding, jumping, falling, and knocked out. Transitions consume the old state and build the next, so illegal moves refuse to compile. A crash calls `knock_out` toward falling, and a platform top calls `land_on` with the surface height. Frame counters such as `IDLE_FRAMES` and `RUNNING_FRAMES` reset on every transition.

## Collision boxes

Every solid exposes `bounding_box()` returning its current `Rect`. Stones store one box; the boy computes his from the live frame trim. Pair tests call `intersects` on the two boxes, true only when both axes overlap. Stone hits route to `knock_out`, platform tops to `land_on`.

## Endless scrolling

A `timeline` cursor marks the right edge of the last segment. While `timeline` stays below `TIMELINE_MINIMUM`, the game appends the next segment at `timeline + OBSTACLE_BUFFER`. Factories such as `stone_and_platform` build each piece; the world moves left per tick and pieces leaving the screen are dropped.

## Web Audio

One `AudioContext` lives in the `Audio` struct for the whole game. Files decode through `decode_audio_data` into `AudioBuffer` clips. Effects fire with `play_sound`, which sources the buffer, connects to the destination, and starts; music loops through the same call.

## Errors and browser tests

Fallible helpers return `anyhow::Result`, and missing DOM nodes become errors via `ok_or_else(|| anyhow!(...))`. Pure logic keeps `cargo test` unit tests. Browser seams take `#[wasm_bindgen_test]` async tests, executed with `wasm-pack test`.
