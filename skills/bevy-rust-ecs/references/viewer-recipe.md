# Viewer recipe: a Bevy 0.19.1 crate that draws a deterministic sim

A complete minimal viewer. It was written from the tagged 0.19.1 sources and examples and was not compiled (the first Bevy build is heavy: use the project's heavy-build queue if it has one; do not build it on a small PC). Every Bevy name below is listed in `verified-api.md`. Where a name there is missing, do not use it.

## Layout

```
<engine repo>/
  Cargo.toml          existing workspace: do not touch it, do not add the viewer to it
  Cargo.lock          existing: do not touch
  crates/sim/         the sim crate: NO bevy dependency (check with scripts/check-sim-outside-bevy.mjs)
  viewer/
    Cargo.toml        its own [workspace] table, depends on sim by path
    Cargo.lock        copy the engine Cargo.lock here once, before the first build
    src/main.rs       Bevy app (below)
    src/sim_port.rs   the ONLY file that names the sim crate (below)
    assets/models/fighter.glb
```

Why its own workspace: Bevy's dev profile settings (needed on Windows, see Gotchas) and its large lock file stay out of the engine workspace, so the sim, the golden hash and every existing crate are byte for byte unchanged. Copying the engine `Cargo.lock` first keeps the sim's dependencies (for example rapier3d) at the locked versions. Cargo keeps locked versions it finds and adds the Bevy ones.

## viewer/Cargo.toml

```toml
[package]
name = "viewer"
version = "0.1.0"
edition = "2024"

[dependencies]
bevy = { version = "0.19.1", default-features = false, features = ["3d"] }
sim = { path = "../crates/sim" }   # use the real path and package name of the sim crate

[features]
dev = ["bevy/dynamic_linking"]     # fast dev builds; never for release

[profile.dev]
opt-level = 1

[profile.dev.package."*"]
opt-level = 3

[workspace]
```

The `3d` profile is `default_app`, `default_platform`, `3d_bevy_render`, `scene`, `picking` (root Cargo.toml line 140). It leaves out `ui` and `audio`. If a name from `bevy::ui` is needed later, add the `ui` feature. Plain `bevy = "0.19.1"` also works and builds more.

## viewer/src/sim_port.rs

The body is a stand-in (two fighters walking in a circle) so the viewer builds before the real sim is wired. Replace the three marked bodies with calls into the sim crate. Nothing outside this file may name a sim type.

```rust
use std::f32::consts::TAU;

/// Plain data the renderer reads. No Bevy types, no sim types.
#[derive(Clone, Copy, Debug, Default)]
pub struct FighterView {
    pub pos: [f32; 3],
    pub yaw: f32, // radians around +Y
    pub anim: u8, // index into the viewer's clip table
}

#[derive(Clone, Debug, Default)]
pub struct Snapshot {
    pub tick: u64,
    pub fighters: Vec<FighterView>,
}

pub struct SimPort {
    tick: u64, // stand-in: hold the sim's state value here
}

impl SimPort {
    pub fn new() -> Self {
        Self { tick: 0 } // REPLACE: build the sim from a fixed seed and a fixed input script
    }

    /// Advance the sim by exactly one tick. Inputs come from a script or replay, never from the keyboard.
    pub fn step(&mut self) {
        self.tick += 1; // REPLACE: call the sim's step
    }

    /// Copy the sim state out. This is the only place where sim numbers become f32.
    pub fn snapshot(&self) -> Snapshot {
        let t = self.tick as f32 / 120.0 * TAU; // REPLACE: read the sim state
        let fighters = (0..2)
            .map(|i| {
                let a = t + i as f32 * TAU / 2.0;
                FighterView { pos: [a.cos() * 3.0, 0.0, a.sin() * 3.0], yaw: -a, anim: 1 }
            })
            .collect();
        Snapshot { tick: self.tick, fighters }
    }
}
```

If the sim state is not `Sync`, keep it out of `Resource` with `app.insert_non_send(..)` and read it with `NonSendMut<T>`.

## viewer/src/main.rs

```rust
use std::time::Duration;

use bevy::{
    prelude::*,
    render::view::screenshot::{save_to_disk, Screenshot, ScreenshotCaptured},
    window::WindowResolution,
    world_serialization::WorldInstanceReady,
};

mod sim_port;
use sim_port::{SimPort, Snapshot};

const FIGHTER_GLB: &str = "models/fighter.glb"; // viewer/assets/models/fighter.glb
/// glTF animation index for each sim animation id: 0 idle, 1 run, 2 attack. Match it to the glb.
const CLIPS: [usize; 3] = [0, 1, 2];
const FIGHTERS: usize = 2;
const TICK_HZ: f64 = 60.0; // the sim's tick rate
const SHOT_TICK: u64 = 120; // take the picture at this sim tick
const TIME_LIMIT_SECS: f32 = 90.0; // give up and exit with an error
const SHOT_PATH: &str = "viewer-shot.png";

fn main() -> AppExit {
    App::new()
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "arena viewer".into(),
                resolution: WindowResolution::new(1280, 720).with_scale_factor_override(1.0),
                ..default()
            }),
            ..default()
        }))
        .add_plugins(ViewerPlugin)
        .run()
}

struct ViewerPlugin;

impl Plugin for ViewerPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(Time::<Fixed>::from_hz(TICK_HZ))
            .insert_resource(GlobalAmbientLight {
                color: Color::WHITE,
                brightness: 1000.0,
                ..default()
            })
            .insert_resource(SimDriver(SimPort::new()))
            .init_resource::<Snapshots>()
            .init_resource::<ShotState>()
            .add_systems(Startup, setup_scene)
            .add_systems(FixedUpdate, step_sim)
            .add_systems(
                Update,
                (apply_snapshot, drive_animation, shot_and_exit).chain(),
            );
    }
}

/// The sim itself. Only `step_sim` touches it.
#[derive(Resource)]
struct SimDriver(SimPort);

/// What the renderer may read: the last two sim states.
#[derive(Resource, Default)]
struct Snapshots {
    prev: Snapshot,
    curr: Snapshot,
}

#[derive(Resource, Default)]
struct ShotState {
    ready: usize,
    requested: bool,
}

/// One animation graph shared by all fighters; `nodes[k]` plays clip `CLIPS[k]`.
#[derive(Resource)]
struct Rig {
    graph: Handle<AnimationGraph>,
    nodes: Vec<AnimationNodeIndex>,
}

/// On the glb root entity: which fighter of the snapshot it shows.
#[derive(Component)]
struct FighterSlot(usize);

/// On the entity that owns the AnimationPlayer.
#[derive(Component)]
struct AnimTarget {
    slot: usize,
    anim: u8,
}

fn setup_scene(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    mut graphs: ResMut<Assets<AnimationGraph>>,
) {
    // Camera3d requires Camera and Projection, so no bundle is needed.
    commands.spawn((
        Camera3d::default(),
        Transform::from_xyz(0.0, 6.0, 12.0).looking_at(Vec3::new(0.0, 1.0, 0.0), Vec3::Y),
    ));
    commands.spawn((
        DirectionalLight {
            shadow_maps_enabled: true,
            ..default()
        },
        Transform::from_xyz(4.0, 10.0, 6.0).looking_at(Vec3::ZERO, Vec3::Y),
    ));
    // Floor.
    commands.spawn((
        Mesh3d(meshes.add(Plane3d::default().mesh().size(20.0, 20.0))),
        MeshMaterial3d(materials.add(Color::srgb(0.3, 0.35, 0.3))),
    ));

    // One graph with one node per clip, built from labelled sub-assets of the glb.
    let clips: Vec<Handle<AnimationClip>> = CLIPS
        .iter()
        .map(|&i| asset_server.load(GltfAssetLabel::Animation(i).from_asset(FIGHTER_GLB)))
        .collect();
    let (graph, nodes) = AnimationGraph::from_clips(clips);
    commands.insert_resource(Rig {
        graph: graphs.add(graph),
        nodes,
    });

    // The fighters. WorldAssetRoot spawns the glb scene as children of this entity.
    for slot in 0..FIGHTERS {
        commands
            .spawn((
                WorldAssetRoot(asset_server.load(GltfAssetLabel::Scene(0).from_asset(FIGHTER_GLB))),
                FighterSlot(slot),
            ))
            .observe(on_fighter_ready);
    }
}

/// Runs once per fighter when its glb scene has been spawned.
fn on_fighter_ready(
    ready: On<WorldInstanceReady>,
    mut commands: Commands,
    rig: Res<Rig>,
    slots: Query<&FighterSlot>,
    children: Query<&Children>,
    mut players: Query<(Entity, &mut AnimationPlayer)>,
    mut shot: ResMut<ShotState>,
) {
    let Ok(slot) = slots.get(ready.entity) else {
        return;
    };
    for child in children.iter_descendants(ready.entity) {
        let Ok((player_entity, mut player)) = players.get_mut(child) else {
            continue;
        };
        let mut transitions = AnimationTransitions::new();
        transitions
            .play(&mut player, rig.nodes[0], Duration::ZERO)
            .repeat();
        commands.entity(player_entity).insert((
            AnimationGraphHandle(rig.graph.clone()),
            transitions,
            AnimTarget { slot: slot.0, anim: 0 },
        ));
        shot.ready += 1;
    }
}

/// The only system that steps the sim. It copies plain data out, nothing else.
fn step_sim(mut sim: ResMut<SimDriver>, mut snaps: ResMut<Snapshots>) {
    sim.0.step();
    snaps.prev = std::mem::take(&mut snaps.curr);
    snaps.curr = sim.0.snapshot();
}

fn v3(p: [f32; 3]) -> Vec3 {
    Vec3::new(p[0], p[1], p[2])
}

/// Move the fighters between the last two sim states. f32 interpolation lives only here.
fn apply_snapshot(
    snaps: Res<Snapshots>,
    fixed: Res<Time<Fixed>>,
    mut fighters: Query<(&FighterSlot, &mut Transform)>,
) {
    let t = fixed.overstep_fraction();
    for (slot, mut tf) in &mut fighters {
        let (Some(a), Some(b)) = (
            snaps.prev.fighters.get(slot.0),
            snaps.curr.fighters.get(slot.0),
        ) else {
            continue;
        };
        tf.translation = v3(a.pos).lerp(v3(b.pos), t);
        tf.rotation = Quat::from_rotation_y(a.yaw).slerp(Quat::from_rotation_y(b.yaw), t);
    }
}

/// Switch the clip when the sim says the fighter changed animation.
fn drive_animation(
    snaps: Res<Snapshots>,
    rig: Res<Rig>,
    mut targets: Query<(&mut AnimTarget, &mut AnimationPlayer, &mut AnimationTransitions)>,
) {
    for (mut target, mut player, mut transitions) in &mut targets {
        let Some(view) = snaps.curr.fighters.get(target.slot) else {
            continue;
        };
        if view.anim == target.anim {
            continue;
        }
        let Some(&node) = rig.nodes.get(view.anim as usize) else {
            continue;
        };
        target.anim = view.anim;
        transitions
            .play(&mut player, node, Duration::from_millis(120))
            .repeat();
    }
}

/// Take one picture at SHOT_TICK, then exit. Give up with an error after TIME_LIMIT_SECS.
fn shot_and_exit(
    mut commands: Commands,
    snaps: Res<Snapshots>,
    mut shot: ResMut<ShotState>,
    time: Res<Time>,
    mut exit: MessageWriter<AppExit>,
) {
    if time.elapsed_secs() > TIME_LIMIT_SECS {
        error!("time limit reached before the screenshot was taken");
        exit.write(AppExit::error());
        return;
    }
    if shot.requested || shot.ready < FIGHTERS || snaps.curr.tick < SHOT_TICK {
        return;
    }
    shot.requested = true;
    commands
        .spawn(Screenshot::primary_window())
        .observe(save_shot_and_exit);
}

fn save_shot_and_exit(captured: On<ScreenshotCaptured>, mut exit: MessageWriter<AppExit>) {
    save_to_disk(SHOT_PATH)(captured);
    exit.write(AppExit::Success);
}
```

## Run

```
# dev build with dynamic linking (heavy the first time: use the heavy-build queue)
cargo run --manifest-path viewer/Cargo.toml --features dev
```

Heavy viewer builds run in the project's heavy-build queue. Never abort the queued wait for a viewer crate build: the first build takes 30 to 60 minutes, so queue every viewer build through the queue and do other tasks meanwhile (an aborted wait still counts as a run: re-queue it instead of starting a bare run). Never run a bare cargo command for the viewer crate: every viewer build uses --locked with a pooled shared cache and --target-dir, plus the queue's sccache and incremental settings. When the queue instructions say to check first with a short command and then the long test, follow that order: then the long test decides; re-queue a run that ends with empty output instead of retrying it by hand on a small PC.

The process exits by itself: code 0 after the picture is saved to `viewer-shot.png` in the current directory, code 1 if the time limit hit first. `fn main() -> AppExit` is what carries the code out.

## Checks before you call it done

1. `node scripts/check-sim-outside-bevy.mjs crates/sim` (and every other existing crate dir) exits 0.
2. The engine's own golden hash check, run in the engine workspace the way it always runs, gives the same hash as before.
3. `git status` shows only new files under `viewer/` (plus the screenshot); no existing file changed.
4. The screenshot file exists and is not one flat colour: look at it, say what is in it.
5. Each plugin crate you added passed `scripts/plugin-bevy-version.mjs` (see SKILL.md).

## Gotchas

- Windows and dynamic linking: without the two `[profile.dev]` blocks the link step can fail with "too many exported symbols" (Bevy setup guide, section Dynamic Linking). Keep them.
- `dynamic_linking` is for dev builds only. A release build must not use it, because the DLLs would have to ship next to the exe (crates/bevy_dylib/src/lib.rs, Warning). Start the program with `cargo run`.
- A glb faces +Z while Bevy forward is -Z (crates/bevy_gltf/src/convert_coordinates.rs). If the fighter shows its back, add a PI turn about Y to the yaw in `apply_snapshot`.
- Pose from wall-clock time is fine for one picture of a looping clip. If two runs must show the same pose at the same tick, set `set_speed(0.0)` on the `ActiveAnimation` (from `AnimationPlayer::animation_mut`) and call `set_seek_time(seconds)` every frame, wrapping `seconds` with `AnimationClip::duration` yourself.
- Clip indexes: `GltfAssetLabel::Animation(i)` uses the position in the glb's `animations` array. To pick clips by name, load the `Gltf` asset, wait for `is_loaded_with_dependencies`, then use `named_animations["Run"]` (see examples/animation/animated_mesh_control.rs in `verified-api.md`).
- Assets are read from `assets/` next to `Cargo.toml` when started with `cargo run`, else next to the exe (`BEVY_ASSET_ROOT` overrides both; crates/bevy_asset/src/io/file/mod.rs lines 19-29).
- The viewer is its own workspace root, so Cargo ignores the `[patch]`, `[replace]` and `[profile]` tables of the engine's root manifest (the sim crate still inherits its own `workspace = true` fields from its own workspace). If the engine root has a `[patch]` or `[replace]`, copy the same lines into `viewer/Cargo.toml`, or the picture is drawn by a different build of the sim's dependencies.
- Inputs to the sim come from a fixed script, so the same ticks always give the same snapshots. The number of fixed steps per rendered frame can differ between runs; that is why the picture is keyed to `SHOT_TICK`, not to a frame number.
- `bevy_ci_testing` (a Bevy feature) can also take a screenshot and exit from a RON file, but it needs the `CI_TESTING_CONFIG` file and a frame number. The code above is simpler.
