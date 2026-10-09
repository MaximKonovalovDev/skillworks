# Patterns

Reusable shapes from MIT code in code/cpp/*.h (structure only, prose omitted).
Source repo: https://github.com/munificent/game-programming-patterns (MIT code only).
Licence: MIT code is free to reuse; chapter prose is NonCommercial, never sold, not included.
Section map: Game Loop and Update Method sit under Sequencing Patterns; Component, Event Queue, Service Locator sit under Decoupling Patterns; Dirty Flag, Object Pool, Spatial Partition, Data Locality sit under Optimization Patterns; Bytecode, Subclass Sandbox, Type Object sit under Behavioral Patterns.
Extra placements: Double Buffer sits under Sequencing Patterns (frame swap); Command, Observer, Singleton sit under Decoupling Patterns; Flyweight sits under Optimization Patterns; State and Prototype helpers sit under Behavioral Patterns.
Full MIT code lives in references/ per-domain files; see their Contents and Sample Code sections. Start with this index, then read only the ONE domain file that matches the task.

## Sequencing Patterns - see `references/sequencing.md`

- 1. Game Loop (code/cpp/game-loop.h): Own the frame with processInput, update, render; sleep with MS_PER_FRAME, pass elapsed, accrue lag for fixed steps.
- 2. Update Method (code/cpp/update-method.h): Entity::update per object; Skeleton patrols x 0..100; Statue waits delay_ then acts.
- 12. Double Buffer (code/cpp/double-buffer.h): Stage actors_[NUM_ACTORS]; Comedian reads wasSlapped and writes slap, then swap.

## Decoupling Patterns - see `references/decoupling.md`

- 3. Component (code/cpp/component.h): Bjorn owns InputComponent, PhysicsComponent, GraphicsComponent; Bjorn::update calls each in order.
- 5. Command (code/cpp/command.h): Command::execute; JumpCommand jump, FireCommand fireGun; InputHandler::handleInput maps BUTTON_X; MoveUnitCommand undo restores xBefore_.
- 7. Observer (code/cpp/observer.h): onNotify(Entity&, Event); Achievements on EVENT_START_FALL; Physics::updateEntity notifies on fall edge.
- 8. Event Queue (code/cpp/event-queue.h): Audio::playSound enqueues PlayMessage into pending_[MAX_PENDING]; update drains via startSound.
- 9. Singleton, carefully (code/cpp/singleton.h): FileSystem::instance; check if (&FileSystem::instance() == NULL) prints singleton is null else singleton is ok.
- 10. Service Locator (code/cpp/service-locator.h): Base::getAudio, Locator::getParticles; Superpower::spawnParticles calls through it.

## Optimization Patterns - see `references/optimization.md`

- 4. Object Pool (code/cpp/object-pool.h): ParticlePool particles_[POOL_SIZE] plus firstAvailable_; create takes head; animate reclaims via setNext.
- 13. Flyweight (code/cpp/flyweight.h): Share Texture and Mesh; per unit keep x, y, health_ only.
- 14. Dirty Flag (code/cpp/dirty-flag.h): GraphNode::render(parentWorld) recomputes world only when local_ changed.
- 15. Spatial Partition (code/cpp/spatial-partition.h): Grid CELL_SIZE 20, cells_[x][y]; add, move, findAt, handleMelee per cell.
- 16. Data Locality (code/cpp/data-locality.h): Thing things[NUM_THINGS] hot loop with doStuff; split cold fields out.

## Behavioral Patterns - see `references/behavioral.md`

- 6. Bytecode VM (code/cpp/bytecode.h): VM::interpret(char bytecode[], int size) switch on bytecode[i]: INST_LITERAL, INST_ADD, INST_SPAWN_PARTICLES.
- 11. State (code/cpp/state.h): Heroine delegates to HeroineState; handleInput swaps StandingState and JumpingState; enter plays art.
- 17. Subclass Sandbox (code/cpp/subclass-sandbox.h): Superpower::spawnParticles plus playSound; subclasses add aim only.
- 18. Type Object (code/cpp/type-object.h): Monster holds Breed& breed_; getAttack uses breed unless health_ < LOW_HEALTH.
- 19. Prototype and Flyweight helpers: Spawner::spawnMonster plus SpawnerFor<T> from code/cpp/prototype.h; Terrain with movementCost, isWater, Texture; World::isWater switches on TERRAIN_GRASS, TERRAIN_HILL, TERRAIN_RIVER.

## License

MIT code is free to reuse; chapter prose is CC BY-NC-ND 4.0, NonCommercial, never sold, not included.
