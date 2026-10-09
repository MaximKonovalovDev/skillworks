# Decoupling Patterns

Section: Decoupling Patterns

Source chapters: book/component.markdown, book/command.markdown, book/observer.markdown, book/event-queue.markdown, book/singleton.markdown, book/service-locator.markdown (structure only, prose omitted).
MIT code: code/cpp/component.h, code/cpp/command.h, code/cpp/observer.h, code/cpp/event-queue.h, code/cpp/singleton.h, code/cpp/service-locator.h (full file plus per-marker blocks in Sample Code).
Source repo: https://github.com/munificent/game-programming-patterns (MIT code only).
Licence: MIT code is free to reuse; chapter prose is NonCommercial, never sold, not included.

## Contents

## What is in this domain
## Sample Code

Section map: Component, Event Queue, Service Locator sit under Decoupling Patterns (patterns.md map). Command, Observer, Singleton also sit here: turn input into objects, react to events, share one instance.

## 3. Component (code/cpp/component.h)

Compose instead of deep inheritance. Bjorn owns InputComponent, PhysicsComponent, GraphicsComponent.
Bjorn::update(World&, Graphics&) calls input_->update(*this), then physics_.update(*this, world), then graphics_.update(*this, graphics).
Swap behavior by passing a new part: new Bjorn(new PlayerInputComponent()) for play, DemoInputComponent for AI.
Use when input, physics, and drawing vary independently.

### Sample Code component

```cpp
Bjorn* bjorn = new Bjorn(new PlayerInputComponent());
class DemoInputComponent : public InputComponent {
public:
  virtual void update(Bjorn& bjorn) {}
};
void Bjorn::update(World& world, Graphics& graphics) {
  input_->update(*this);
  physics_.update(*this, world);
  graphics_.update(*this, graphics);
}
```

## 5. Command (code/cpp/command.h)

Turn input into objects. Command base has execute(); JumpCommand calls actor jump(), FireCommand calls fireGun().
InputHandler::handleInput checks isPressed(BUTTON_X) then BUTTON_Y then BUTTON_A and runs the matching command.
MoveUnitCommand adds undo(): execute() does unit_->moveTo(x_, y_); undo() does unit_->moveTo(xBefore_, yBefore_).
Use when input, AI, and replays must all drive the same actions, or moves need undo.

### Sample Code command

```cpp
class Command { public: virtual void execute() = 0; };
void InputHandler::handleInput() {
  if (isPressed(BUTTON_X)) jump();
  else if (isPressed(BUTTON_Y)) fireGun();
  else if (isPressed(BUTTON_A)) swapWeapon();
}
void MoveUnitCommand::execute() { unit_->moveTo(x_, y_); }
void MoveUnitCommand::undo() { unit_->moveTo(xBefore_, yBefore_); }
```

## 7. Observer (code/cpp/observer.h)

Decouple events from reactions. Observer has onNotify(Entity&, Event). Achievements::onNotify unlocks when event == EVENT_START_FALL.
Physics::updateEntity compares wasOnSurface to isOnSurface after accelerate(GRAVITY) and update(), then calls notify(entity, EVENT_START_FALL) on the fall edge.
Use when many systems react to one event. Do not do heavy work inside onNotify.

### Sample Code observer

```cpp
class Observer {
public:
  virtual void onNotify(const Entity& entity, Event event) = 0;
};
void Physics::updateEntity(Entity& entity) {
  bool wasOnSurface = entity.isOnSurface();
  entity.accelerate(GRAVITY);
  entity.update();
  if (wasOnSurface && !entity.isOnSurface()) notify(entity, EVENT_START_FALL);
}
```

## 8. Event Queue (code/cpp/event-queue.h)

Delay delivery to a safe point. Audio::playSound(id, volume) writes a PlayMessage into pending_[MAX_PENDING] at tail_; update() reads at head_ and calls startSound(resource, channel, volume), then advances head_ = (head_ + 1) % MAX_PENDING.
Use for sound and UI events raised during update. Ring drops or asserts when full; size it for the peak frame.

### Sample Code event-queue

```cpp
static PlayMessage pending_[MAX_PENDING];
static int head_;
static int tail_;
void Audio::playSound(SoundId id, int volume) {
  pending_[tail_].id = id;
  pending_[tail_].volume = volume;
  tail_ = (tail_ + 1) % MAX_PENDING;
}
void Audio::update() {
  startSound(pending_[head_].id, pending_[head_].volume);
  head_ = (head_ + 1) % MAX_PENDING;
}
```

## 9. Singleton, carefully (code/cpp/singleton.h)

One instance with a global point of access. FileSystem::instance() builds once and returns it. The sample checks if (&FileSystem::instance() == NULL) to print singleton is null else singleton is ok.
Prefer passing the instance in, or a locator, over calling instance() deep in code. Lazy init hides startup cost and order.
Use only when one instance is a real constraint (file system, audio device). A null here means never built.

### Sample Code singleton

```cpp
FileSystem& FileSystem::instance() {
  static FileSystem* instance = new FileSystem();
  return *instance;
}
if (&FileSystem::instance() == NULL) std::cout << "singleton is null!" << std::endl;
else std::cout << "singleton is ok" << std::endl;
```

## 10. Service Locator (code/cpp/service-locator.h)

Provide a service without hardwiring it. Base::getAudio() returns *service_; Locator::getParticles() returns the shared ParticleSystem.
Superpower::spawnParticles(type, count) calls through the locator so powers never news their own systems.
Use when many callers need audio, particles, or debug draw. Set the service at startup so tests can swap a null or mock service.

### Sample Code service-locator

```cpp
class Base {
protected:
  static Audio& getAudio() { return *service_; }
private:
  static Audio* service_;
};
ParticleSystem& Locator::getParticles() { return particles; }
void Superpower::spawnParticles(ParticleType type, int count) {
  Locator::getParticles().spawn(type, count);
}
```

## License

Code blocks above are MIT (Robert Nystrom, code/cpp/*.h).
Chapter prose is CC BY-NC-ND 4.0, NonCommercial, never sold, not included.
