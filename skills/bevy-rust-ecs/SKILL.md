---
name: bevy-rust-ecs
description: Bevy VIEWER dropped 2026-10-07 (owner "i dont want bevy shit i want my own renderer"): do not build or extend a Bevy viewer. Stealing Bevy code and methods into our own renderer (crates/render) stays fine. Old text - Bevy 0.19.1 for a coding agent that builds a viewer crate drawing a deterministic sim - ECS app basics, loading a glTF or glb fighter, skeletal animation with AnimationPlayer and AnimationGraph, snapshot resources, dynamic linking, screenshots, plugin version pins. Use when writing or fixing Bevy code, editing a Cargo.toml bevy dependency, or when a Bevy tutorial from 0.12 to 0.16 does not compile on bevy 0.19.
license: MIT OR Apache-2.0 (Bevy source), MIT (scaffold)
---

# bevy-rust-ecs

> Bevy VIEWER dropped 2026-10-07 (owner: "i dont want bevy shit i want my own renderer"; later the same day:
> "we steal from bevy just stuff"). The viewer is frozen and the picture is our own renderer in `crates/render`.
> Do not build or extend a viewer. Reading Bevy source and stealing its methods into `crates/render` stays fine.

Target: Bevy 0.19.1 (stable; 0.20 is only a release candidate, do not use it). Old tutorials are wrong in many names. Before you write a Bevy name you are unsure of, find it in `references/verified-api.md`. Everything here was read from the v0.19.1 source, none of it compiled.

## Old names that no longer exist
- `SceneRoot` is now `WorldAssetRoot`; `SceneInstanceReady` is `WorldInstanceReady` (import it from `bevy::world_serialization`). `bevy::scene` is the new BSN system and cannot spawn glTF yet.
- No bundles: `Camera3dBundle`, `PbrBundle`, `SceneBundle`, `DirectionalLightBundle` are gone. Spawn a tuple of components; required components add `Transform`, `Visibility`, `Camera`.
- `EventReader`, `EventWriter`, `add_event` are now `MessageReader`, `MessageWriter` (`.write(..)`), `add_message`. Observers take `On<E>`, not `Trigger<E>`.
- `AnimationPlayer::play` takes an `AnimationNodeIndex` from an `AnimationGraph`; the player entity also needs an `AnimationGraphHandle`.
- `get_single()` is now `single()` (a Result); `Input<KeyCode>` is `ButtonInput<KeyCode>`; the ambient light resource is `GlobalAmbientLight`; `delta_seconds()` is `delta_secs()`; `despawn_recursive()` is `despawn()`.
- One type cannot derive both `Component` and `Resource` (a Resource is a Component now).

## Smallest working scene: glb + animation
```rust
use bevy::{prelude::*, world_serialization::WorldInstanceReady};

const GLB: &str = "models/fighter.glb"; // file: assets/models/fighter.glb

fn main() -> AppExit {
    App::new().add_plugins(DefaultPlugins).add_systems(Startup, setup).run()
}

#[derive(Component)]
struct Clips { graph: Handle<AnimationGraph>, idle: AnimationNodeIndex }

fn setup(mut commands: Commands, assets: Res<AssetServer>,
         mut graphs: ResMut<Assets<AnimationGraph>>,
         mut meshes: ResMut<Assets<Mesh>>, mut mats: ResMut<Assets<StandardMaterial>>) {
    commands.spawn((Camera3d::default(),
        Transform::from_xyz(0.0, 4.0, 8.0).looking_at(Vec3::ZERO, Vec3::Y)));
    commands.spawn((DirectionalLight::default(),
        Transform::from_xyz(3.0, 8.0, 4.0).looking_at(Vec3::ZERO, Vec3::Y)));
    commands.spawn((Mesh3d(meshes.add(Plane3d::default().mesh().size(20.0, 20.0))),
        MeshMaterial3d(mats.add(Color::srgb(0.3, 0.4, 0.3)))));
    let (graph, idle) = AnimationGraph::from_clip(
        assets.load(GltfAssetLabel::Animation(0).from_asset(GLB)));
    commands.spawn((
        WorldAssetRoot(assets.load(GltfAssetLabel::Scene(0).from_asset(GLB))),
        Clips { graph: graphs.add(graph), idle },
    )).observe(play_idle);
}

fn play_idle(ready: On<WorldInstanceReady>, mut commands: Commands, clips: Query<&Clips>,
             children: Query<&Children>, mut players: Query<&mut AnimationPlayer>) {
    let Ok(clips) = clips.get(ready.entity) else { return };
    for e in children.iter_descendants(ready.entity) {
        if let Ok(mut player) = players.get_mut(e) {
            player.play(clips.idle).repeat();
            commands.entity(e).insert(AnimationGraphHandle(clips.graph.clone()));
        }
    }
}
```
The glTF loader puts the `AnimationPlayer` on a descendant of the scene root, so wait for `WorldInstanceReady` and search `iter_descendants`. With several clips use `AnimationGraph::from_clips` and `AnimationTransitions` (switch with `transitions.play(&mut player, node, Duration)`). Full crate: `references/viewer-recipe.md`.

## ECS in five lines
- `Startup` runs once, `Update` every frame, `FixedUpdate` at a fixed step (64 Hz default; `Time::<Fixed>::from_hz(60.0)`). Order systems with `(a, b).chain()`.
- A system is a plain fn with `Commands`, `Query<&mut T, With<U>>`, `Res<T>`, `ResMut<T>`, `Single<..>`.
- `#[derive(Component)]` data lives on entities; `#[derive(Resource)]` is global (`init_resource`, `insert_resource`).
- Messages (`#[derive(Message)]`, `add_message::<M>()`) are buffered and read later by `MessageReader`. Events (`#[derive(Event)]`, `EntityEvent`) go to observers at once (`.observe(f)`, `add_observer(f)`).
- A plugin is `impl Plugin for X { fn build(&self, app: &mut App) }`.

## Keep the deterministic sim outside Bevy
1. The sim crate has no `bevy*` dependency. Check: `node scripts/check-sim-outside-bevy.mjs <sim crate dir> [<other crate dir> ...]` (exit 1 lists offenders, also renames and `workspace = true`).
2. The viewer is a new crate in its own `[workspace]` (e.g. `viewer/`), depending on the sim by path and on `bevy = "0.19.1"`. Do not add it to the engine workspace or edit the engine lock; seed `viewer/Cargo.lock` from it.
3. One system in `FixedUpdate` owns the sim, steps it, and copies plain data (f32, no sim types) into a `Snapshots` Resource (prev and curr). All other systems only read it. Bevy never writes sim state. Feed the sim a fixed input script, never live keys.
4. Interpolate `Transform` from prev and curr in `Update` with `Time<Fixed>::overstep_fraction()`.
5. rapier3d stays inside the sim: no `bevy_rapier`.
6. Done means: golden hash check unchanged, only `viewer/` is new in git, checker exit 0, a screenshot you looked at.

## Dev setup
- Fast dev builds: feature `dynamic_linking`. In the viewer: `[features] dev = ["bevy/dynamic_linking"]`, run `cargo run --features dev`. Dev only. On Windows also set `[profile.dev] opt-level = 1` and `[profile.dev.package."*"] opt-level = 3`, else the link fails with "too many exported symbols".
- The first Bevy build is heavy (many minutes, several GB). Do not build it on a small PC: use the project's heavy-build queue if it has one.
- Heavy viewer builds run in the queue: queue every viewer build there; see `references/viewer-recipe.md` Run section for the queued-wait rules.
- Smaller build: `bevy = { version = "0.19.1", default-features = false, features = ["3d"] }`.
- Assets live in `assets/` next to Cargo.toml (`cargo run` reads there).
- A glb faces +Z, Bevy forward is -Z: if the fighter shows its back, turn it by PI about Y.
- Screenshot then exit (`use bevy::render::view::screenshot::{save_to_disk, Screenshot, ScreenshotCaptured};`):
```rust
commands.spawn(Screenshot::primary_window()).observe(save_and_exit);

fn save_and_exit(shot: On<ScreenshotCaptured>, mut exit: MessageWriter<AppExit>) {
    save_to_disk("shot.png")(shot); // file format comes from the extension
    exit.write(AppExit::Success);
}
```
- Time limit: in a system, `if time.elapsed_secs() > 90.0 { exit.write(AppExit::error()); }`. `fn main() -> AppExit` returns the exit code. Take the shot at a sim tick, not a frame number.

## Plugin version pin
A plugin crate (bevy_hanabi, bevy-inspector-egui, bevy_brp_mcp, bevy_ggrs, bevy_mod_inverse_kinematics ...) works with one Bevy minor. Before `cargo add`: `node scripts/plugin-bevy-version.mjs owner/repo` (for a workspace repo `owner/repo:crate/dir`). It reads `bevy = ".."` in Cargo.toml on the default branch and at the latest release tag, plus the README compatibility table, and prints OK, NO or UNKNOWN against 0.19.1. The default branch often targets 0.20; the release tag decides. Never add a plugin on NO.

## Files
- `references/viewer-recipe.md`: complete viewer crate (Cargo.toml, sim_port.rs, main.rs, checks, gotchas).
- `references/verified-api.md`: every Bevy name with file and line at v0.19.1, and the names that do not exist.
- `references/sources.md`: sources, licences, pinned tag and commit.
- `scripts/check-sim-outside-bevy.mjs`, `scripts/plugin-bevy-version.mjs`: Node 24, no install.
