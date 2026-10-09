# Sequencing Patterns

Section: Sequencing Patterns

Source chapters: book/game-loop.markdown, book/update-method.markdown, book/double-buffer.markdown (structure only, prose omitted).
MIT code: code/cpp/game-loop.h, code/cpp/update-method.h, code/cpp/double-buffer.h (full file plus per-marker blocks in Sample Code).
Source repo: https://github.com/munificent/game-programming-patterns (MIT code only).
Licence: MIT code is free to reuse; chapter prose is NonCommercial, never sold, not included.

## Contents

## What is in this domain
## Sample Code

Section map: Game Loop and Update Method sit under Sequencing Patterns (patterns.md map). Double Buffer also sits here: read last frame, write next frame, then swap.

## 1. Game Loop (code/cpp/game-loop.h)

Own the frame. One loop calls processInput, update, render in order.
Start fixed: while true with sleep(start + MS_PER_FRAME - now).
Then variable: pass elapsed = current - lastTime into update(elapsed).
Then fixed-step: accrue lag += elapsed; while lag >= STEP update(STEP).
Use when the game must advance in real time. Do not let render set game state.

### Sample Code game-loop

```cpp
double start = getCurrentTime();
processInput();
update();
render();
sleep(start + MS_PER_FRAME - getCurrentTime());
double lastTime = getCurrentTime();
double current = getCurrentTime();
double elapsed = current - lastTime;
processInput();
update(elapsed);
render();
double lag = 0.0;
lag += elapsed;
while (lag >= STEP) { update(STEP); lag -= STEP; }
```

## 2. Update Method (code/cpp/update-method.h)

Split per-frame work into Entity::update(). The loop calls update on each entity.
Skeleton::update patrols: if patrollingLeft_ setX(x() - 1), flip at 0 and 100.
Statue::update counts delay_ frames, then fires once.
Use when many objects simulate each frame. Keep each update small; never edit the entity list while iterating it.

### Sample Code update-method

```cpp
class Skeleton : public Entity {
public:
  virtual void update() {
    if (patrollingLeft_) {
      setX(x() - 1);
      if (x() == 0) patrollingLeft_ = false;
    } else {
      setX(x() + 1);
      if (x() == 100) patrollingLeft_ = true;
    }
  }
private:
  bool patrollingLeft_;
};
class Statue : public Entity {
public:
  Statue(int delay) : delay_(delay) {}
  virtual void update() { if (--delay_ == 0) fire(); }
private:
  int delay_;
};
```

## 12. Double Buffer (code/cpp/double-buffer.h)

Read last frame, write next frame, then swap. Stage holds Actor* actors_[NUM_ACTORS]. Comedian::update reads wasSlapped() from the read side and calls facing_->slap() on the write side.
No actor sees a half-updated frame.
Use when updates read neighbor state (flocking, cellular motion). The swap itself costs one pointer exchange.

### Sample Code double-buffer

```cpp
class Comedian : public Actor {
public:
  virtual void update() {
    if (wasSlapped()) facing_->slap();
  }
private:
  Actor* facing_;
};
```

## License

Code blocks above are MIT (Robert Nystrom, code/cpp/*.h).
Chapter prose is CC BY-NC-ND 4.0, NonCommercial, never sold, not included.
