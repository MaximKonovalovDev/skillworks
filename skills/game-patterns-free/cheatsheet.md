# Cheatsheet

One-page recall from MIT code in code/cpp/*.h (structure only, prose omitted).
Full listing: chapters/notes.md Contents and Sample Code. Source: https://github.com/munificent/game-programming-patterns (MIT code).
Licence: MIT code free to reuse; chapter prose NonCommercial, never sold, not included.
Section map: Sequencing Patterns holds Game Loop plus Update Method.

- loop: while (running) { processInput(); update(); render(); } Sleep start + MS_PER_FRAME - now; or pass elapsed; or accrue lag for fixed steps.
- update: Entity::update() per object. Skeleton patrols x 0..100; Statue waits delay_ then acts. Never edit the list while updating.
- component: Bjorn(InputComponent* input) with PhysicsComponent plus GraphicsComponent. Bjorn::update(World&, Graphics&) calls input, physics, graphics in order. Swap with new PlayerInputComponent or DemoInputComponent.
- pool: ParticlePool particles_[POOL_SIZE] plus firstAvailable_. create() takes head; animate() reclaims via setNext(). Cap is fixed; init false means full.
- command: Command::execute(). InputHandler::handleInput maps BUTTON_X to jump(), BUTTON_Y to fireGun(). MoveUnitCommand undo() restores xBefore_, yBefore_.
- bytecode: VM::interpret(char bytecode[], int size) switch on bytecode[i]: INST_LITERAL, INST_ADD, INST_SPAWN_PARTICLES.
- observer: onNotify(Entity&, Event). Physics posts EVENT_START_FALL on the fall edge; Achievements listens.
- event queue: Audio::playSound(id, volume) enqueues PlayMessage into pending_[MAX_PENDING]; update() drains via startSound().
- singleton: FileSystem::instance(); check if (&FileSystem::instance() == NULL) prints singleton is null else singleton is ok. Prefer inject over global.
- locator: Base::getAudio(), Locator::getParticles(). Superpower::spawnParticles(type, count) calls through it.
- state: Heroine delegates to HeroineState. handleInput swaps StandingState and JumpingState; enter() plays art, update() moves.
- double buffer: Stage actors_[NUM_ACTORS]; read wasSlapped(), write slap(), then swap buffers.
- flyweight: share Texture and Mesh; per unit keep x, y, health_ only.
- dirty flag: GraphNode::render(parentWorld) recomputes world only when local_ changed.
- spatial: Grid CELL_SIZE 20, cells_[x][y]; add(), move(), findAt(x, y), handleMelee() per cell.
- locality: Thing things[NUM_THINGS] hot loop; split cold fields out.
- sandbox: Superpower::spawnParticles plus playSound; subclasses add aim only.
- type object: Monster holds Breed& breed_; getAttack() uses breed unless health_ < LOW_HEALTH. New types add a Breed row, no subclass.
- where: code/cpp holds each header; chapters/notes.md keeps structure only headings plus MIT code blocks.
