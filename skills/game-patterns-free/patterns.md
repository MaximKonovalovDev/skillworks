# Patterns

Reusable shapes from MIT code in code/cpp/*.h (structure only, prose omitted).
See chapters/notes.md Contents and Sample Code sections for the full MIT code listing.
Source repo: https://github.com/munificent/game-programming-patterns (MIT code only).
Licence: MIT code is free to reuse; chapter prose is NonCommercial, never sold, not included.
Section map: Game Loop and Update Method sit under Sequencing Patterns; Component, Event Queue, Service Locator sit under Decoupling Patterns; Dirty Flag, Object Pool, Spatial Partition, Data Locality sit under Optimization Patterns; Bytecode, Subclass Sandbox, Type Object sit under Behavioral Patterns.

## 1. Game Loop (code/cpp/game-loop.h)

Own the frame. One loop calls processInput, update, render in order.
Start fixed: while true with sleep(start + MS_PER_FRAME - now).
Then variable: pass elapsed = current - lastTime into update(elapsed).
Then fixed-step: accrue lag += elapsed; while lag >= STEP update(STEP).
Use when the game must advance in real time. Do not let render set game state.

## 2. Update Method (code/cpp/update-method.h)

Split per-frame work into Entity::update(). The loop calls update on each entity.
Skeleton::update patrols: if patrollingLeft_ setX(x() - 1), flip at 0 and 100.
Statue::update counts delay_ frames, then fires once.
Use when many objects simulate each frame. Keep each update small; never edit the entity list while iterating it.

## 3. Component (code/cpp/component.h)

Compose instead of deep inheritance. Bjorn owns InputComponent, PhysicsComponent, GraphicsComponent.
Bjorn::update(World&, Graphics&) calls input_->update(*this), then physics_.update(*this, world), then graphics_.update(*this, graphics).
Swap behavior by passing a new part: new Bjorn(new PlayerInputComponent()) for play, DemoInputComponent for AI.
Use when input, physics, and drawing vary independently.

## 4. Object Pool (code/cpp/object-pool.h)

Reuse fixed slots, never news per frame. ParticlePool holds Particle particles_[POOL_SIZE] plus firstAvailable_.
create(x, y, xVel, yVel, lifetime) takes the head of the free list; animate() steps live particles and pushes dead ones back with setNext(firstAvailable_).
Particle hides inUse_ and next; only the pool touches them.
Use when spawn rate is high (particles, bullets). Fixed size caps memory; init() returns false when full.

## 5. Command (code/cpp/command.h)

Turn input into objects. Command base has execute(); JumpCommand calls actor jump(), FireCommand calls fireGun().
InputHandler::handleInput checks isPressed(BUTTON_X) then BUTTON_Y then BUTTON_A and runs the matching command.
MoveUnitCommand adds undo(): execute() does unit_->moveTo(x_, y_); undo() does unit_->moveTo(xBefore_, yBefore_).
Use when input, AI, and replays must all drive the same actions, or moves need undo.

## 6. Bytecode VM (code/cpp/bytecode.h)

Data beats code for content moves. VM::interpret(char bytecode[], int size) loops i over size, reads instruction = bytecode[i], switch-dispatches INST_LITERAL, INST_GET_HEALTH, INST_ADD, INST_SPAWN_PARTICLES.
Each case does a small stack or spawn step, then breaks back to the loop.
Use when designers tune behavior without recompiling. Keep the instruction set tiny; the front end that emits bytecode is separate work.

## 7. Observer (code/cpp/observer.h)

Decouple events from reactions. Observer has onNotify(Entity&, Event). Achievements::onNotify unlocks when event == EVENT_START_FALL.
Physics::updateEntity compares wasOnSurface to isOnSurface after accelerate(GRAVITY) and update(), then calls notify(entity, EVENT_START_FALL) on the fall edge.
Use when many systems react to one event. Do not do heavy work inside onNotify.

## 8. Event Queue (code/cpp/event-queue.h)

Delay delivery to a safe point. Audio::playSound(id, volume) writes a PlayMessage into pending_[MAX_PENDING] at tail_; update() reads at head_ and calls startSound(resource, channel, volume), then advances head_ = (head_ + 1) % MAX_PENDING.
Use for sound and UI events raised during update. Ring drops or asserts when full; size it for the peak frame.

## 9. Singleton, carefully (code/cpp/singleton.h)

One instance with a global point of access. FileSystem::instance() builds once and returns it. The sample checks if (&FileSystem::instance() == NULL) to print singleton is null else singleton is ok.
Prefer passing the instance in, or a locator, over calling instance() deep in code. Lazy init hides startup cost and order.
Use only when one instance is a real constraint (file system, audio device). A null here means never built.

## 10. Service Locator (code/cpp/service-locator.h)

Provide a service without hardwiring it. Base::getAudio() returns *service_; Locator::getParticles() returns the shared ParticleSystem.
Superpower::spawnParticles(type, count) calls through the locator so powers never news their own systems.
Use when many callers need audio, particles, or debug draw. Set the service at startup so tests can swap a null or mock service.

## 11. State (code/cpp/state.h)

Replace switch spaghetti with objects. Heroine holds HeroineState*; handleInput(Input) asks the state for the next state; update(Heroine&) runs per-frame motion.
StandingState, JumpingState each implement handleInput and update; enter(Heroine&) plays the matching Animate.
Use when input means different things per pose (stand, jump, duck). Static state instances avoid news per switch.

## 12. Double Buffer (code/cpp/double-buffer.h)

Read last frame, write next frame, then swap. Stage holds Actor* actors_[NUM_ACTORS]. Comedian::update reads wasSlapped() from the read side and calls facing_->slap() on the write side.
No actor sees a half-updated frame.
Use when updates read neighbor state (flocking, cellular motion). The swap itself costs one pointer exchange.

## 13. Flyweight (code/cpp/flyweight.h)

Share what repeats. One Texture, Mesh, or Breed object serves hundreds of units; each unit keeps only x, y, health_.
Use when instance count explodes. Split shared (intrinsic) from per-unit (extrinsic) data.

## 14. Dirty Flag (code/cpp/dirty-flag.h)

Skip work that did not change. GraphNode::render(Transform parentWorld) combines local_ with parent only when the dirty flag is set, caches world, clears the flag; children reuse the cached world.
Use for scene graphs and derived data. Set the flag on every write path or stale data ships.

## 15. Spatial Partition (code/cpp/spatial-partition.h)

Only test neighbors. Grid with CELL_SIZE 20 and cells_[x][y]; add(unit), move(unit, x, y), findAt(x, y). handleMelee() walks each cell and calls handleCell, which calls handleUnit only on units in that cell.
Use when N units would otherwise need N-squared checks. Keep cell size near the melee range.

## 16. Data Locality (code/cpp/data-locality.h)

Keep hot data together. Thing things[NUM_THINGS] stepped in one for loop with doStuff(); cold fields split into a separate array so the hot loop stays in cache.
Use when the profiler names update loops. Pack, do not pad, the hot struct.

## 17. Subclass Sandbox (code/cpp/subclass-sandbox.h)

Give powers a safe toolbox. Superpower base offers spawnParticles(ParticleType, int) and playSound(SoundId); SkyLaunch, GroundDive subclasses call them plus their own aim code.
Use when many sibling abilities share a few engine calls. Keep sandbox methods small and stable; powers never touch engine globals directly.

## 18. Type Object (code/cpp/type-object.h)

A class for a class. Monster holds Breed& breed_ with movementCost_, isWater, Texture. Monster::getAttack() returns breed_.getAttack() unless health_ < LOW_HEALTH, then a weak flail line.
SpawnerFor<Ghost> style templates build variants without new subclasses.
Use when content authors add dozens of unit types. Track breed objects in one table; constructors on the type object keep init in one place.

## 19. Prototype and Flyweight helpers

Spawner::spawnMonster() plus SpawnerFor<T> covers spawn functions and templates from code/cpp/prototype.h. Terrain(int movementCost, bool isWater, Texture) covers enum-to-class data splits from code/cpp/flyweight.h and type splits. World::isWater(x, y) switches on TERRAIN_GRASS, TERRAIN_HILL, TERRAIN_RIVER.
Use when spawn or terrain rules change per level. Clone the prototype, then tweak fields; never branch the spawner on type names.
