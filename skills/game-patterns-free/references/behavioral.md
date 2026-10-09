# Behavioral Patterns

Section: Behavioral Patterns

Source chapters: book/bytecode.markdown, book/state.markdown, book/subclass-sandbox.markdown, book/type-object.markdown, book/prototype.markdown (structure only, prose omitted).
MIT code: code/cpp/bytecode.h, code/cpp/state.h, code/cpp/subclass-sandbox.h, code/cpp/type-object.h, code/cpp/prototype.h (full file plus per-marker blocks in Sample Code).
Source repo: https://github.com/munificent/game-programming-patterns (MIT code only).
Licence: MIT code is free to reuse; chapter prose is NonCommercial, never sold, not included.

## Contents

## What is in this domain
## Sample Code

Section map: Bytecode, Subclass Sandbox, Type Object sit under Behavioral Patterns (patterns.md map). State and Prototype helpers also sit here: swap behavior by object, clone to spawn.

## 6. Bytecode VM (code/cpp/bytecode.h)

Data beats code for content moves. VM::interpret(char bytecode[], int size) loops i over size, reads instruction = bytecode[i], switch-dispatches INST_LITERAL, INST_GET_HEALTH, INST_ADD, INST_SPAWN_PARTICLES.
Each case does a small stack or spawn step, then breaks back to the loop.
Use when designers tune behavior without recompiling. Keep the instruction set tiny; the front end that emits bytecode is separate work.

### Sample Code bytecode

```cpp
void VM::interpret(char bytecode[], int size) {
  for (int i = 0; i < size; i++) {
    char instruction = bytecode[i];
    switch (instruction) {
      case INST_LITERAL: break;
      case INST_GET_HEALTH: break;
      case INST_ADD: break;
      case INST_SPAWN_PARTICLES: break;
    }
  }
}
```

## 11. State (code/cpp/state.h)

Replace switch spaghetti with objects. Heroine holds HeroineState*; handleInput(Input) asks the state for the next state; update(Heroine&) runs per-frame motion.
StandingState, JumpingState each implement handleInput and update; enter(Heroine&) plays the matching Animate.
Use when input means different things per pose (stand, jump, duck). Static state instances avoid news per switch.

### Sample Code state

```cpp
class HeroineState {
public:
  virtual void handleInput(Heroine& heroine, Input input) {}
  virtual void update(Heroine& heroine) {}
  virtual void enter(Heroine& heroine) {}
};
class StandingState : public HeroineState {};
class JumpingState : public HeroineState {};
```

## 17. Subclass Sandbox (code/cpp/subclass-sandbox.h)

Give powers a safe toolbox. Superpower base offers spawnParticles(ParticleType, int) and playSound(SoundId); SkyLaunch, GroundDive subclasses call them plus their own aim code.
Use when many sibling abilities share a few engine calls. Keep sandbox methods small and stable; powers never touch engine globals directly.

### Sample Code subclass-sandbox

```cpp
class Superpower {
protected:
  void spawnParticles(ParticleType type, int count) {
    ParticleSystem& particles = Locator::getParticles();
    particles.spawn(type, count);
  }
  void playSound(SoundId id) {}
};
class SkyLaunch : public Superpower {};
class GroundDive : public Superpower {};
```

## 18. Type Object (code/cpp/type-object.h)

A class for a class. Monster holds Breed& breed_ with movementCost_, isWater, Texture. Monster::getAttack() returns breed_.getAttack() unless health_ < LOW_HEALTH, then a weak flail line.
SpawnerFor<Ghost> style templates build variants without new subclasses.
Use when content authors add dozens of unit types. Track breed objects in one table; constructors on the type object keep init in one place.

### Sample Code type-object

```cpp
class Breed {
public:
  const char* getAttack() { return "attack"; }
private:
  int movementCost_;
  bool isWater_;
  Texture texture_;
};
const char* Monster::getAttack() {
  if (health_ < LOW_HEALTH) return "The monster flails weakly.";
  return breed_.getAttack();
}
```

## 19. Prototype and Flyweight helpers

Spawner::spawnMonster() plus SpawnerFor<T> covers spawn functions and templates from code/cpp/prototype.h. Terrain(int movementCost, bool isWater, Texture) covers enum-to-class data splits from code/cpp/flyweight.h and type splits. World::isWater(x, y) switches on TERRAIN_GRASS, TERRAIN_HILL, TERRAIN_RIVER.
Use when spawn or terrain rules change per level. Clone the prototype, then tweak fields; never branch the spawner on type names.

### Sample Code prototype

```cpp
class Spawner {
public:
  virtual Monster* spawnMonster() = 0;
};
template <class T>
class SpawnerFor : public Spawner {
public:
  virtual Monster* spawnMonster() { return new T(); }
};
Spawner* ghostSpawner = new SpawnerFor<Ghost>();
class Terrain {
public:
  Terrain(int movementCost, bool isWater, Texture texture) {}
};
bool World::isWater(int x, int y) {
  switch (tiles_[x][y]) {
    case TERRAIN_GRASS: return false;
    case TERRAIN_HILL: return false;
    case TERRAIN_RIVER: return true;
  }
  return false;
}
```

## License

Code blocks above are MIT (Robert Nystrom, code/cpp/*.h).
Chapter prose is CC BY-NC-ND 4.0, NonCommercial, never sold, not included.
