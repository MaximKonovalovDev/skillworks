---
name: rust-wasm-game
description: Use when wiring Rust to the browser for a game: wasm-bindgen boot, canvas sprites, the requestAnimationFrame loop, RedHatBoy-style state machines, bounding-box collision, endless-runner timelines, Web Audio, and wasm-pack tests.
version: 0.1.0
author: skillworks
tags: []
license: MIT
---

# Rust and WebAssembly game patterns

Rules distilled from Eric Smith, Game Development with Rust and WebAssembly (Packt, 2022) for running Rust on the web while building a game. Each rule names the exact token to type and where it goes. Longer notes live in `references/patterns.md`, the one-page reminder in `references/cheatsheet.md`, and provenance in `references/sources.md`. No book text is copied; only short terms appear, in own words.

## Boot the wasm module

- Mark the entry with `#[wasm_bindgen(start)]` so the browser runs it on load.
- Log with `console::log_1(&JsValue::from_str("loaded"))` while bringing the module up.
- Call `console_error_panic_hook::set_once()` once at boot so Rust panics read well in the console.
- Load assets inside a `browser::spawn_local` async block; the game starts when the block resolves.

## Draw on the canvas

- Grab the canvas with `get_element_by_id("canvas")` and cast it to `HtmlCanvasElement`.
- Take its 2d handle as `CanvasRenderingContext2d` and pass it into a small `Renderer` wrapper.
- All drawing goes through the `Renderer`, never through raw context calls in game code.

## Cut sprite sheets with serde

- Model the atlas JSON with `Sheet` and `Cell` structs derived with `serde`.
- Read each frame trim from `spriteSourceSize` so transparent padding never sizes a sprite.
- Keep one shared sheet plus the image, and hand both to every sprite that needs them.

## Load images without blocking

- Build each bitmap with `HtmlImageElement::new()` and point it at its file with `set_src`.
- Fetch JSON atlases with `JsFuture::from` over `fetch`, then `await` the promise into text.
- Hang the onload callback with `unchecked_ref` and pin it with `forget()` until it fires.

## Run the frame loop

- Declare `type LoopClosure = Closure<dyn FnMut(f64)>` for the per-frame callback.
- Hold the live callback as `SharedLoopClosure`, an `Rc` of `RefCell` over `Option<LoopClosure>`.
- Re-queue every frame with `request_animation_frame` from inside the callback itself.

## Split update from draw

- Describe each screen with `trait Game`, carrying `initialize`, `update`, and `draw`.
- Step logic on a fixed tick: `FRAME_SIZE` is one sixtieth of a second in milliseconds.
- Add real elapsed time into `accumulated_delta`, run `update` while it exceeds the tick, then draw once.

## Read the keyboard

- Listen for `keydown` and `keyup` on the window, each delivering a `KeyboardEvent`.
- Reduce the event stream into a `KeyState` holding `pressed_keys`, a map from code to event.
- Ask `contains_key(code)` for held keys; insert on down, remove on up.

## Animate with a state machine

- Wrap every pose in the `RedHatBoyStateMachine` enum: idle, running, sliding, jumping, falling, knocked out.
- Move between poses with consuming transitions; a crash calls `knock_out` into falling.
- Land with `land_on(y)`, feeding the platform top so the feet stop exactly on it.
- Count frames per pose (`IDLE_FRAMES`, `RUNNING_FRAMES`) and reset the count on each transition.

## Collide with boxes

- Give every solid thing a `Rect` and expose it through `bounding_box()`.
- Test pairs with `intersects(&Rect)`, which is true only when both axes overlap.
- On a stone hit call `knock_out`; on a platform top call `land_on` with the box top.
- Draw the boxes while tuning, then keep the same `Rect` the art uses.

## Scroll an endless runner

- Keep a `timeline` cursor at the right edge of the last placed segment.
- When `timeline` drops below `TIMELINE_MINIMUM`, append the next segment at `timeline + OBSTACLE_BUFFER`.
- Build segments from factories like `stone_and_platform`, move the world left each tick, and drop what leaves the screen.

## Play sound through Web Audio

- Create one `AudioContext` for the game and keep it in an `Audio` struct.
- Decode files with `decode_audio_data` into `AudioBuffer` values wrapped as `Sound` clips.
- Fire effects with `play_sound`, which builds a buffer source, connects it to the destination, and starts it; music loops down the same path.

## Fail loudly and test in a browser

- Return `anyhow::Result` from fallible helpers, turn missing DOM nodes into errors with `ok_or_else(|| anyhow!(...))`.
- Keep pure logic (boxes, timelines, frame counts) in plain functions with `cargo test` unit tests.
- Cover browser seams with `#[wasm_bindgen_test]` async tests and run them with `wasm-pack test`.
- Ship the bundle with continuous deployment once the suite is green.

Recall sheet: `references/cheatsheet.md`. Provenance: `references/sources.md`.
