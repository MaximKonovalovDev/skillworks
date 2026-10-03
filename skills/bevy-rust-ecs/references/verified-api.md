# Verified API: Bevy 0.19.1

Pinned tag `v0.19.1`, commit `b56fc29d3016e641754765244b5ba3f9cc504671`, repo `bevyengine/bevy`. Every path is in that repo at that tag; the number is the line where the item is defined, or where an example uses it. Nothing here was compiled. Each row was found by reading the tagged source.

## Verified names

### App and schedules

| Item | File:line at v0.19.1 | Note |
|---|---|---|
| `App` | `crates/bevy_app/src/app.rs:85` |  |
| `App::new` | `crates/bevy_app/src/app.rs:139` |  |
| `App::add_plugins` | `crates/bevy_app/src/app.rs:655` | takes one plugin or a tuple of plugins |
| `App::add_systems` | `crates/bevy_app/src/app.rs:321` |  |
| `App::insert_resource` | `crates/bevy_app/src/app.rs:451` |  |
| `App::init_resource` | `crates/bevy_app/src/app.rs:485` | needs `FromWorld` (Default is enough) |
| `App::add_message` | `crates/bevy_app/src/app.rs:427` | replaces `add_event` |
| `App::add_observer` | `crates/bevy_app/src/app.rs:1474` | global observer |
| `App::insert_non_send` | `crates/bevy_app/src/app.rs:516` | for `!Sync` data; `insert_non_send_resource` is deprecated since 0.19.0 (line 492) |
| `App::run` | `crates/bevy_app/src/app.rs:185` | returns `AppExit` |
| `Plugin` | `crates/bevy_app/src/plugin.rs:57` | `fn build(&self, app: &mut App)` |
| `DefaultPlugins` | `crates/bevy_internal/src/default_plugins.rs:5` | includes `AnimationPlugin` (line 85); window, render, asset, gltf by feature |
| `PluginGroupBuilder::set` | `crates/bevy_app/src/plugin_group.rs:312` | used as `DefaultPlugins.set(WindowPlugin { .. })` |
| `Startup` | `crates/bevy_app/src/main_schedule.rs:69` | runs once |
| `Update` | `crates/bevy_app/src/main_schedule.rs:173` | every frame |
| `FixedUpdate` | `crates/bevy_app/src/main_schedule.rs:133` | 0..n times per frame at the fixed timestep |
| `AppExit` | `crates/bevy_app/src/app.rs:1560` | `AppExit::Success`; it is itself a `Message` |
| `AppExit::error` | `crates/bevy_app/src/app.rs:1572` | exit code 1 |
| `Termination for AppExit` | `crates/bevy_app/src/app.rs:1608` | `fn main() -> AppExit` works; the process exit code follows |
| `IntoScheduleConfigs::chain` | `crates/bevy_ecs/src/schedule/config.rs:471` | `(a, b, c).chain()` runs them in order |

### ECS types

| Item | File:line at v0.19.1 | Note |
|---|---|---|
| `Commands` | `crates/bevy_ecs/src/system/commands/mod.rs:105` |  |
| `Commands::spawn` | `crates/bevy_ecs/src/system/commands/mod.rs:398` | takes a tuple of components |
| `Commands::entity` | `crates/bevy_ecs/src/system/commands/mod.rs:439` |  |
| `Commands::insert_resource` | `crates/bevy_ecs/src/system/commands/mod.rs:895` |  |
| `Commands::write_message` | `crates/bevy_ecs/src/system/commands/mod.rs:1217` | queues a `Message` (for example `AppExit`) |
| `EntityCommands::insert` | `crates/bevy_ecs/src/system/commands/mod.rs:1435` |  |
| `EntityCommands::observe` | `crates/bevy_ecs/src/system/commands/mod.rs:2071` | attach an entity observer |
| `Entity` | `crates/bevy_ecs/src/entity/mod.rs:424` |  |
| `Query` | `crates/bevy_ecs/src/system/query.rs:487` |  |
| `Query::get` | `crates/bevy_ecs/src/system/query.rs:1577` | returns `Result` |
| `Query::get_mut` | `crates/bevy_ecs/src/system/query.rs:1713` | returns `Result` |
| `Query::single` | `crates/bevy_ecs/src/system/query.rs:2097` | returns `Result`; there is no `get_single` |
| `Query::single_mut` | `crates/bevy_ecs/src/system/query.rs:2126` | returns `Result` |
| `Query::iter_descendants` | `crates/bevy_ecs/src/relationship/relationship_query.rs:101` | call it on a `Query<&Children>` |
| `Single` | `crates/bevy_ecs/src/system/query.rs:2850` | system parameter; the system is skipped when there is not exactly one match |
| `Res` | `crates/bevy_ecs/src/change_detection/params.rs:462` |  |
| `ResMut` | `crates/bevy_ecs/src/change_detection/params.rs:535` |  |
| `NonSendMut` | `crates/bevy_ecs/src/change_detection/params.rs:620` | system parameter for `!Sync` data inserted with `App::insert_non_send` |
| `Children` | `crates/bevy_ecs/src/hierarchy.rs:152` | relationship target with `linked_spawn` (line 148): despawning a parent despawns its children |
| `Component` | `crates/bevy_ecs/src/component/mod.rs:511` | `#[derive(Component)]` is `derive_component` at crates/bevy_ecs/macros/src/lib.rs:828 |
| `Resource` | `crates/bevy_ecs/src/resource.rs:87` | a Resource is now also a Component: never derive both on one type; `derive_resource` at crates/bevy_ecs/macros/src/lib.rs:586 |
| `Message` | `crates/bevy_ecs/src/message/mod.rs:100` | buffered, polled; `derive_message` at crates/bevy_ecs/macros/src/lib.rs:561 |
| `MessageWriter` | `crates/bevy_ecs/src/message/message_writer.rs:62` |  |
| `MessageWriter::write` | `crates/bevy_ecs/src/message/message_writer.rs:74` | was `EventWriter::send` |
| `MessageReader` | `crates/bevy_ecs/src/message/message_reader.rs:34` | `.read()` iterates unread messages |
| `Event` | `crates/bevy_ecs/src/event/mod.rs:88` | instant, observer driven |
| `EntityEvent` | `crates/bevy_ecs/src/event/mod.rs:327` | an event aimed at one entity (has an `entity` field) |
| `On` | `crates/bevy_ecs/src/observer/system_param.rs:38` | first parameter of an observer function; derefs to the event |
| `Commands::trigger` | `crates/bevy_ecs/src/system/commands/mod.rs:1169` | fires an `Event` at observers |

### Time

| Item | File:line at v0.19.1 | Note |
|---|---|---|
| `Time` | `crates/bevy_time/src/time.rs:192` |  |
| `Time::elapsed_secs` | `crates/bevy_time/src/time.rs:306` | was `elapsed_seconds` |
| `Time::delta_secs` | `crates/bevy_time/src/time.rs:283` | was `delta_seconds` |
| `Fixed` | `crates/bevy_time/src/fixed.rs:69` | `Time<Fixed>`; default step is 64 Hz (line 76) |
| `Time::from_hz` | `crates/bevy_time/src/fixed.rs:105` | on `Time<Fixed>`: `insert_resource(Time::<Fixed>::from_hz(60.0))` |
| `Time::overstep_fraction` | `crates/bevy_time/src/fixed.rs:205` | on `Time<Fixed>`; 0.0..1.0 progress toward the next fixed step: the interpolation factor |

### Scene, camera, light, mesh, math

| Item | File:line at v0.19.1 | Note |
|---|---|---|
| `Transform` | `crates/bevy_transform/src/components/transform.rs:86` | fields `translation`, `rotation`, `scale` |
| `Transform::from_xyz` | `crates/bevy_transform/src/components/transform.rs:119` |  |
| `Transform::looking_at` | `crates/bevy_transform/src/components/transform.rs:187` |  |
| `Camera3d` | `crates/bevy_camera/src/components.rs:25` | `#[require(Camera, Projection)]` (line 24): no bundle needed; forward is -Z |
| `Mesh3d` | `crates/bevy_mesh/src/components.rs:102` | `#[require(Transform)]` (line 101) |
| `MeshMaterial3d` | `crates/bevy_pbr/src/mesh_material.rs:41` |  |
| `StandardMaterial` | `crates/bevy_pbr/src/pbr_material.rs:26` |  |
| `Mesh` | `crates/bevy_mesh/src/mesh.rs:227` |  |
| `Plane3d` | `crates/bevy_math/src/primitives/dim3.rs:103` | primitive shape |
| `Meshable::mesh` | `crates/bevy_mesh/src/primitives/mod.rs:39` | in the mesh prelude |
| `PlaneMeshBuilder::size` | `crates/bevy_mesh/src/primitives/dim3/plane.rs:89` |  |
| `DirectionalLight` | `crates/bevy_light/src/directional_light.rs:73` | requires `Transform` and `Visibility` (attribute at line 63); field `shadow_maps_enabled` |
| `PointLight` | `crates/bevy_light/src/point_light.rs:48` |  |
| `GlobalAmbientLight` | `crates/bevy_light/src/ambient_light.rs:62` | the ambient light Resource; fields `color`, `brightness` |
| `AmbientLight` | `crates/bevy_light/src/ambient_light.rs:12` | a per-camera Component (`#[require(Camera)]`), not the global Resource |
| `ClearColor` | `crates/bevy_camera/src/clear_color.rs:55` | Resource; background colour |
| `Color` | `crates/bevy_color/src/color.rs:56` | `Color::srgb(..)` and `Color::WHITE` are used in the examples listed below |
| `Vec3` | `crates/bevy_math/src/lib.rs:84` | glam type re-exported by the math prelude |
| `Quat` | `crates/bevy_math/src/lib.rs:83` | glam type re-exported by the math prelude |
| `Vec3::lerp` | `examples/3d/parallax_mapping.rs:196` | glam method, example line |
| `Quat::slerp` | `examples/3d/parallax_mapping.rs:197` | glam method, example line |
| `Quat::from_rotation_y` | `examples/3d/atmosphere.rs:248` | glam method, example line |
| `Vec3::new` | `examples/animation/animated_mesh.rs:109` | glam method, example line; the same line uses `Vec3::Y` |
| `Vec3::ZERO` | `examples/window/screenshot.rs:77` | glam constants, example line |
| `default` | `crates/bevy_utils/src/lib.rs:71` | `..default()` in struct literals |

### Assets, glTF, scene spawning

| Item | File:line at v0.19.1 | Note |
|---|---|---|
| `AssetServer` | `crates/bevy_asset/src/server/mod.rs:66` |  |
| `AssetServer::load` | `crates/bevy_asset/src/server/mod.rs:364` | returns a `Handle<A>` at once; loading is async |
| `Assets` | `crates/bevy_asset/src/assets.rs:288` |  |
| `Assets::add` | `crates/bevy_asset/src/assets.rs:401` | returns a `Handle` |
| `Assets::get` | `crates/bevy_asset/src/assets.rs:430` |  |
| `Handle` | `crates/bevy_asset/src/handle.rs:134` | not a Component |
| `WorldAssetRoot` | `crates/bevy_world_serialization/src/components.rs:23` | `#[require(Transform)]` and `#[require(Visibility)]` (lines 21-22); was `SceneRoot` |
| `WorldAsset` | `crates/bevy_world_serialization/src/world_asset.rs:23` | was `Scene`; the asset type of a glTF scene handle |
| `WorldInstanceReady` | `crates/bevy_world_serialization/src/world_asset_spawner.rs:33` | EntityEvent with field `entity`; import it from `bevy::world_serialization`, it is not in the prelude |
| `GltfAssetLabel` | `crates/bevy_gltf/src/label.rs:33` | in the prelude |
| `GltfAssetLabel::Scene` | `crates/bevy_gltf/src/label.rs:35` |  |
| `GltfAssetLabel::Animation` | `crates/bevy_gltf/src/label.rs:60` | index = position in the glTF animations array |
| `GltfAssetLabel::from_asset` | `crates/bevy_gltf/src/label.rs:112` | returns an `AssetPath` |
| `Gltf` | `crates/bevy_gltf/src/assets.rs:18` | fields `default_scene` (line 40) and `named_animations` (line 46) |
| `GltfMaterial` | `crates/bevy_gltf/src/material.rs:14` | a `#MaterialN` sub-asset now loads as this; add the `/std` suffix to get a `StandardMaterial` (migration guide) |

### Animation

| Item | File:line at v0.19.1 | Note |
|---|---|---|
| `AnimationClip` | `crates/bevy_animation/src/lib.rs:105` |  |
| `AnimationClip::duration` | `crates/bevy_animation/src/lib.rs:254` | seconds |
| `AnimationPlayer` | `crates/bevy_animation/src/lib.rs:732` | the glTF loader adds it to the scene entity that owns the skinned rig (doc comment above the struct) |
| `AnimationPlayer::play` | `crates/bevy_animation/src/lib.rs:866` | takes a graph node index, not a clip handle |
| `AnimationPlayer::animation_mut` | `crates/bevy_animation/src/lib.rs:983` |  |
| `ActiveAnimation` | `crates/bevy_animation/src/lib.rs:509` |  |
| `ActiveAnimation::repeat` | `crates/bevy_animation/src/lib.rs:641` | loop forever |
| `ActiveAnimation::set_speed` | `crates/bevy_animation/src/lib.rs:666` |  |
| `ActiveAnimation::set_seek_time` | `crates/bevy_animation/src/lib.rs:697` | sets the pose time without firing events |
| `AnimationGraph` | `crates/bevy_animation/src/graph.rs:114` | an Asset: keep it in `Assets<AnimationGraph>` |
| `AnimationGraph::from_clip` | `crates/bevy_animation/src/graph.rs:445` | returns the graph and one node index |
| `AnimationGraph::from_clips` | `crates/bevy_animation/src/graph.rs:458` | returns the graph and a Vec of node indices, in input order |
| `AnimationGraphHandle` | `crates/bevy_animation/src/graph.rs:138` | Component: insert it on the entity that has the `AnimationPlayer` |
| `AnimationNodeIndex` | `crates/bevy_animation/src/graph.rs:161` | Copy |
| `AnimationTransitions` | `crates/bevy_animation/src/transition.rs:33` | Component |
| `AnimationTransitions::new` | `crates/bevy_animation/src/transition.rs:68` |  |
| `AnimationTransitions::play` | `crates/bevy_animation/src/transition.rs:78` | start animations through this when the component is present, not through the player |
| `AnimationPlugin` | `crates/bevy_animation/src/lib.rs:1278` | part of `DefaultPlugins` |

### Screenshot, window, logging

| Item | File:line at v0.19.1 | Note |
|---|---|---|
| `Screenshot` | `crates/bevy_render/src/view/window/screenshot.rs:80` | spawn it as an entity; import from `bevy::render::view::screenshot` |
| `Screenshot::primary_window` | `crates/bevy_render/src/view/window/screenshot.rs:98` |  |
| `ScreenshotCaptured` | `crates/bevy_render/src/view/window/screenshot.rs:49` | EntityEvent that carries the `Image` |
| `save_to_disk` | `crates/bevy_render/src/view/window/screenshot.rs:134` | writes the file inside the observer; the format comes from the file extension |
| `Window` | `crates/bevy_window/src/window.rs:164` | field `title: String`, field `resolution` (line 172) |
| `WindowPlugin` | `crates/bevy_window/src/lib.rs:64` | field `primary_window: Option<Window>` |
| `WindowResolution` | `crates/bevy_window/src/window.rs:895` | import from `bevy::window`, it is not in the prelude |
| `WindowResolution::new` | `crates/bevy_window/src/window.rs:923` |  |
| `WindowResolution::with_scale_factor_override` | `crates/bevy_window/src/window.rs:932` | pin to 1.0 so the screenshot has the same pixel size on every screen |
| `error` | `crates/bevy_log/src/lib.rs:36` | log macro `error!`, in the prelude |

### Cargo features (root Cargo.toml)

| Item | File:line at v0.19.1 | Note |
|---|---|---|
| `dynamic_linking` | `Cargo.toml:280` | use `cargo run --features bevy/dynamic_linking`; docs in crates/bevy_dylib/src/lib.rs lines 7-35 |
| `3d profile` | `Cargo.toml:140` | `default_app`, `default_platform`, `3d_bevy_render`, `scene`, `picking`: enough for a viewer |
| `3d_bevy_render` | `Cargo.toml:241` | includes `bevy_gltf`, `bevy_pbr`, `gltf_animation` |
| `default features` | `Cargo.toml:134` | `2d`, `3d`, `ui`, `audio` |
| `bevy_ci_testing` | `Cargo.toml:554` | config-driven `ScreenshotAndExit` (crates/bevy_dev_tools/src/ci_testing/config.rs:43); needs a RON file |

### Usage patterns taken from examples and crate code

| Pattern | File:line |
|---|---|
| Load a glb scene: `WorldAssetRoot(asset_server.load(GltfAssetLabel::Scene(0).from_asset(PATH)))` | `examples/animation/animated_mesh.rs:58` |
| Graph from one labelled clip: `AnimationGraph::from_clip(asset_server.load(GltfAssetLabel::Animation(2)..))` | `examples/animation/animated_mesh.rs:41` |
| Observer fires when the scene is spawned: `.observe(f)` with `On<WorldInstanceReady>` | `examples/animation/animated_mesh.rs:64` |
| Find the player: `children.iter_descendants(scene_ready.entity)` then `players.get_mut(child)` | `examples/animation/animated_mesh.rs:81` |
| Start and loop: `player.play(index).repeat()` | `examples/animation/animated_mesh.rs:88` |
| Attach the graph: `.insert(AnimationGraphHandle(handle.clone()))` | `examples/animation/animated_mesh.rs:94` |
| Floor: `Mesh3d(meshes.add(Plane3d::default().mesh().size(..)))` + `MeshMaterial3d(materials.add(Color::srgb(..)))` | `examples/animation/animated_mesh.rs:114` |
| Light: `DirectionalLight { shadow_maps_enabled: true, ..default() }` | `examples/animation/animated_mesh.rs:121` |
| Ambient: `insert_resource(GlobalAmbientLight { color, brightness, ..default() })` | `examples/animation/animated_mesh.rs:14` |
| Camera: `(Camera3d::default(), Transform::from_xyz(..).looking_at(..))` | `examples/animation/animated_mesh.rs:108` |
| Several clips plus transitions: `AnimationTransitions::new()` then `transitions.play(&mut player, node, Duration::ZERO).repeat()` | `examples/animation/animated_mesh_control.rs:149` |
| One player in the world: `player: Single<(Entity, &mut AnimationPlayer)>` | `examples/animation/animated_mesh_control.rs:146` |
| Clips by name: `fox.named_animations["Run"].clone()` (needs the `Gltf` asset loaded first) | `examples/animation/animated_mesh_control.rs:115` |
| Screenshot to a file: `commands.spawn(Screenshot::primary_window()).observe(save_to_disk(path))` | `examples/window/screenshot.rs:26` |
| Screenshot then exit (closure observer with `MessageWriter<AppExit>`) | `crates/bevy_dev_tools/src/ci_testing/systems.rs:27` |
| Write an exit: `app_exit_writer.write(AppExit::Success)` | `examples/app/headless_renderer.rs:516` |
| Fixed step: `.add_systems(FixedUpdate, f)` and `.insert_resource(Time::<Fixed>::from_seconds(0.5))` | `examples/ecs/fixed_timestep.rs:13` |
| Window size: `DefaultPlugins.set(WindowPlugin { primary_window: Some(Window { resolution: WindowResolution::new(1920, 1080).with_scale_factor_override(1.0), ..default() }), ..default() })` | `examples/gizmos/2d_text_gizmos.rs:23` |
| Window title: `Window { title: "..".into(), .. }` | `examples/window/window_settings.rs:20` |
| Messages: `#[derive(Message)]`, `MessageWriter<T>`, `.write(..)`, `MessageReader<T>`, `.read()` | `examples/ecs/message.rs:9` |
| Error log: `error!(..)` | `examples/ecs/system_piping.rs:26` |
| Wait for load: `asset_server.is_loaded_with_dependencies(&handle)` | `examples/animation/animated_mesh_control.rs:104` |

## Names that do NOT exist in 0.19.1

Each name below has no code hit anywhere in `crates/`, `examples/`, `tests/`, `benches/`, `tools/` or `src/` at the tag (comment lines are ignored; a script counted them). Do not write them.

| Old name | Use instead | Code hits at the tag |
|---|---|---|
| `SceneRoot` | `WorldAssetRoot` (renamed in 0.19; only a doc comment remembers the old name, crates/bevy_world_serialization/src/components.rs:15) | 0 |
| `SceneInstanceReady` | `WorldInstanceReady` (`bevy::world_serialization::WorldInstanceReady`) | 0 |
| `DynamicScene, DynamicSceneBuilder, DynamicSceneRoot` | `DynamicWorld`, `DynamicWorldBuilder`, `DynamicWorldRoot` | 0 |
| `EventReader` | `MessageReader` (buffered messages); for instant events use an observer with `On<E>` | 0 |
| `EventWriter` | `MessageWriter` and `.write(..)` (was `.send(..)`) | 0 |
| `App::add_event` | `App::add_message::<M>()` | 0 |
| `Events<T>` | `Messages<M>` | 0 |
| `Trigger<E> as an observer parameter` | `On<E>`; `Trigger` is now an unsafe trait for event delivery (crates/bevy_ecs/src/event/trigger.rs:38) | 0 |
| `Camera3dBundle` | spawn `(Camera3d::default(), Transform::..)`; `Camera3d` requires `Camera` and `Projection` | 0 |
| `Camera2dBundle` | spawn `Camera2d` | 0 |
| `PbrBundle, MaterialMeshBundle` | spawn `(Mesh3d(handle), MeshMaterial3d(handle), Transform::..)` | 0 |
| `SceneBundle` | spawn `WorldAssetRoot(handle)` | 0 |
| `DirectionalLightBundle, PointLightBundle, SpotLightBundle` | spawn `(DirectionalLight { .. }, Transform::..)` | 0 |
| `SpriteBundle, TextBundle, NodeBundle, ImageBundle, ButtonBundle` | spawn the components directly: `Sprite`, `Text`, `Node`, `ImageNode` | 0 |
| `Query::get_single, get_single_mut` | `single()` and `single_mut()` (both return `Result`), or the `Single<D>` parameter | 0 |
| `Input<KeyCode>` | `ButtonInput<KeyCode>` (crates/bevy_input/src/button_input.rs:125) | 0 |
| `bevy::prelude::shape (shape::Cube, shape::Plane ..)` | primitives: `Cuboid`, `Plane3d`, `Sphere`, then `meshes.add(Cuboid::new(1.0, 1.0, 1.0))` | 0 |
| `despawn_recursive` | `despawn()` (children are despawned too) | 0 |
| `App::add_plugin (singular)` | `add_plugins(..)` | 0 |
| `Time::delta_seconds, elapsed_seconds` | `delta_secs()`, `elapsed_secs()` | 0 |
| `AnimationPlayer::play_with_transition` | `AnimationTransitions::play(&mut player, node, duration)` | 0 |
| `spawn_bundle` | `spawn` | 0 |

### Things that still exist but behave differently

| Thing | What changed in 0.19 | Evidence |
|---|---|---|
| `#[derive(Component, Resource)]` on one type | no longer allowed: a Resource is now a Component too, so split into two types | `Resource: Component` at crates/bevy_ecs/src/resource.rs:87; migration guide "Resources as Components" |
| `Scene` | now a BSN trait; the old asset type is `WorldAsset`; the new `bevy::scene` cannot spawn glTF yet | crates/bevy_scene/src/scene.rs:48; migration guide section "The old bevy_scene is now bevy_world_serialization" |
| `AmbientLight` | a per-camera Component; the global one is the `GlobalAmbientLight` Resource | crates/bevy_light/src/ambient_light.rs:12 and crates/bevy_light/src/ambient_light.rs:62 |
| `asset_server.load("x.glb#Material0")` | loads a `GltfMaterial`; ask for `"x.glb#Material0/std"` to get a `StandardMaterial` | migration guide "Invert `bevy_gltf` dependency with `bevy_pbr`" |
| `ui` and `audio` features | no longer implied by `3d`; the default features still carry all four | Cargo.toml:134; migration guide "`audio` feature is now no longer implied" |
| `Replace` lifecycle event | renamed `Discard` | migration guide "Lifecycle event changes" |
| glTF scene forward axis | glTF faces +Z, Bevy forward is -Z; a fighter may face away from the camera: rotate the root by PI around Y | crates/bevy_gltf/src/convert_coordinates.rs:41 |
