# Glossary

Terms below come from MIT code in code/cpp/*.h (structure only, prose omitted).
Full MIT code listing lives in references/ per-domain files (sequencing, decoupling, optimization, behavioral); see their Contents and Sample Code sections. Start with patterns.md index.
Source repo: https://github.com/munificent/game-programming-patterns (MIT code, book prose excluded).
Licence note: MIT code is free to reuse; chapter prose is NonCommercial, never sold, not included.

- game loop: the while(running) frame driver in code/cpp/game-loop.h. Calls processInput then update then render each frame. Variants clamp with MS_PER_FRAME sleep, pass elapsed time, or accrue lag for fixed steps.
- Sequencing Patterns: the section that groups Game Loop and Update Method. Game Loop owns the frame; Update Method splits per-entity work into update() slices.
- update method: Entity::update() in code/cpp/update-method.h. Each entity advances itself one frame. Example Skeleton patrols x between 0 and 100; Statue waits delay frames then acts.
- game object: base Entity with x(), setX(), update(). Skeleton and Statue subclass it and override update().
- component: code/cpp/component.h. Bjorn holds InputComponent plus PhysicsComponent plus GraphicsComponent and calls each update in Bjorn::update(World&, Graphics&).
- Bjorn: the sample hero entity. Built as new Bjorn(new PlayerInputComponent()). Swaps input by passing a new InputComponent, e.g. DemoInputComponent for AI control.
- InputComponent: interface with update(Bjorn&). PlayerInputComponent reads buttons; DemoInputComponent drives Bjorn with no input.
- PhysicsComponent: moves Bjorn, applies velocity_, calls world.resolveCollision(volume_, x_, y_, velocity_), picks a Sprite by walk direction.
- GraphicsComponent: draws Bjorn with graphics.draw(sprite, x, y). BjornGraphicsComponent is one concrete drawer.
- command: code/cpp/command.h. Command base has execute(). JumpCommand, FireCommand wrap one action. InputHandler::handleInput maps BUTTON_X to jump(), BUTTON_Y to fireGun(), BUTTON_A to swapWeapon().
- undo command: MoveUnitCommand stores unit_, xBefore_, yBefore_, x_, y_. execute() calls unit_->moveTo(x_, y_); undo() calls unit_->moveTo(xBefore_, yBefore_).
- bytecode: code/cpp/bytecode.h. VM::interpret(char bytecode[], int size) loops the array and switch-dispatches each instruction such as INST_LITERAL, INST_ADD, INST_SPAWN_PARTICLES.
- interpret: the VM loop body. Reads instruction = bytecode[i], switches on it, runs the matching case, then continues to the next byte.
- object pool: code/cpp/object-pool.h. ParticlePool holds Particle particles_[POOL_SIZE] plus firstAvailable_. create() reuses a free slot; animate() returns dead particles to the free list via setNext().
- particle: pooled struct with x, y, xVel, yVel, lifetime, inUse_, next pointer. animate() returns true when lifetime ends so the pool can reclaim it.
- observer: code/cpp/observer.h. Observer base has onNotify(Entity&, Event). Achievements unlocks on EVENT_START_FALL; Physics::updateEntity notifies when wasOnSurface and now airborne.
- prototype: code/cpp/prototype.h. Spawner base has spawnMonster(). SpawnerFor<T> template returns new T(), e.g. new SpawnerFor<Ghost>().
- singleton: code/cpp/singleton.h. FileSystem::instance() returns the one instance. Sample test checks if (&FileSystem::instance() == NULL) and prints singleton is null versus singleton is ok.
- null: the empty-pointer check above. A null instance means the singleton was never built; ok means it exists.
- service locator: code/cpp/service-locator.h. Locator::getParticles() or Base::getAudio() returns the shared service. Superpower::spawnParticles() calls through it so powers stay decoupled.
- event queue: code/cpp/event-queue.h. Audio::playSound(id, volume) enqueues a PlayMessage into pending_[MAX_PENDING] ring with head_ and tail_; update() drains one entry per call via startSound().
- double buffer: code/cpp/double-buffer.h. Stage holds Actor* actors_[NUM_ACTORS]; Comedian::update reads wasSlapped() from the read buffer and writes slap() to the write buffer, then buffers swap.
- flyweight: code/cpp/flyweight.h. Shares one Texture or Mesh across many units instead of one copy per unit; split intrinsic state (shared art) from extrinsic state (per-unit x, y).
- dirty flag: code/cpp/dirty-flag.h. GraphNode caches world transform; render(parentWorld) recomputes only when local_ changed, else reuses the cached value.
- spatial partition: code/cpp/spatial-partition.h. Grid with CELL_SIZE 20 and cells_[x][y]. add(), move(), findAt(x, y), handleMelee() only test units in the same or neighbor cells.
- data locality: code/cpp/data-locality.h. Thing things[NUM_THINGS] updated in one tight for loop so hot data stays in cache; cold data split out of the loop.
- state: code/cpp/state.h. Heroine delegates to HeroineState. handleInput swaps state objects (StandingState, JumpingState); enter() runs on entry, update() runs per frame.
- subclass sandbox: code/cpp/subclass-sandbox.h. Superpower base offers sandbox methods spawnParticles(type, count) and playSound(id); each power subclass calls them and adds its own moves.
- type object: code/cpp/type-object.h. Monster holds Breed& breed_. getAttack() returns breed_.getAttack() unless health_ is below LOW_HEALTH, then it flails weakly. New monsters need only a new Breed, no new subclass.
