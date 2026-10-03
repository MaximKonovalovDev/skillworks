# Sources and licences (verified 2026-10-03)

Everything in this skill was written in my own words and my own code from the sources below. API names are short facts and are quoted as names only. Nothing was compiled; every claim is backed by a file and line in `verified-api.md`.

## 1. Bevy engine source at tag v0.19.1

- URL: https://github.com/bevyengine/bevy/tree/v0.19.1
- Pinned tag: `v0.19.1`, published 2026-08-13T00:02:58Z. It is the latest stable release (`gh api repos/bevyengine/bevy/releases/latest`, checked 2026-10-03).
- Pinned commit: `b56fc29d3016e641754765244b5ba3f9cc504671` (`gh api repos/bevyengine/bevy/git/ref/tags/v0.19.1`; the source archive of the tag unpacks to `bevyengine-bevy-b56fc29`).
- Licence, verified live on 2026-10-03: `MIT OR Apache-2.0`. Evidence: `license = "MIT OR Apache-2.0"` in the root Cargo.toml (line 10); LICENSE-MIT (MIT License text) and LICENSE-APACHE (Apache License 2.0 text) both read at the tag; the README License section says all code is dual-licensed under MIT or Apache-2.0 (lines 103-113). The GitHub licence API shows `apache-2.0` for the repository (GitHub reports one of the two).
- Taken: type, function, feature and file names; line numbers; the shape of the usage patterns in `crates/` and `examples/` (animation, gltf, window, ecs, app). No code was copied; the recipe is new code that uses the same API.
- Files read: `Cargo.toml`, `docs/cargo_features.md`, `.cargo/config_fast_builds.toml`, `crates/bevy_app`, `crates/bevy_ecs`, `crates/bevy_animation`, `crates/bevy_gltf`, `crates/bevy_world_serialization`, `crates/bevy_render` (screenshot), `crates/bevy_dev_tools` (ci_testing), `crates/bevy_dylib`, `crates/bevy_time`, `crates/bevy_window`, `crates/bevy_asset`, plus `examples/animation/animated_mesh.rs`, `animated_mesh_control.rs`, `examples/gltf/load_gltf.rs`, `examples/window/screenshot.rs`, `examples/ecs/message.rs`, `fixed_timestep.rs`, `examples/app/headless_renderer.rs`.
- The `main` branch is `0.20.0-dev` and the tags `v0.20.0-rc.1` and `v0.20.0-rc.2` are pre-releases (checked with `gh api repos/bevyengine/bevy/tags` and `releases`). Read the tag, not `main`, and not docs for 0.20.

## 2. Bevy website: migration guide, release notes, setup guide

- URLs:
  - https://bevy.org/learn/migration-guides/0-18-to-0-19/ (source file `content/learn/migration-guides/0.18-to-0.19.md`, last commit `ff249dbc3615301fcde63a18bafd8aadae62bc91`, 2026-06-19)
  - https://bevy.org/news/bevy-0-19/ (source file `content/news/2026-06-19-bevy-0.19/index.md`, last commit `412933161d467de9722278e651569801bcda0953`, 2026-06-20)
  - https://bevy.org/learn/quick-start/getting-started/setup/ (source file `content/learn/quick-start/getting-started/setup.md`, last commit `aaaab5068cb20b7a4acc01874e0a25bd001b0858`, 2026-06-19)
  - Repository: https://github.com/bevyengine/bevy-website
- Licence, verified live on 2026-10-03: the repository LICENSE is the MIT License (Copyright 2020 Bevy Engine) and the GitHub licence API says `MIT`. No separate content licence is stated in its README.md or CONTRIBUTING.md.
- Taken: facts only, in my own words: the 0.19 renames (`SceneRoot` to `WorldAssetRoot`, `SceneInstanceReady` to `WorldInstanceReady`), Resources as Components, the `ui` and `audio` feature split, the glTF material change, and the Windows dynamic linking note.

## 3. Third-party plugin crates named in the version rule

`bevy_hanabi`, `bevy-inspector-egui`, `bevy_brp_mcp`, `bevy_ggrs` and `bevy_mod_inverse_kinematics` are named only as examples of crates to check. None of their code or text is used. Run `scripts/plugin-bevy-version.mjs` to read their live Cargo.toml.

## What is not verified

- Nothing was compiled or run. The first Bevy build is heavy and was not started.
- The Cargo workspace statements in `viewer-recipe.md` (the viewer has its own `[workspace]` next to the engine, a path dependency across workspaces, `[patch]` of the engine root being ignored, a lock file seeded from the engine lock keeping the locked versions) are standard Cargo behaviour, not Bevy behaviour, and were not run here.
- Starting the dynamically linked exe by hand (outside `cargo run`) was not tested.
