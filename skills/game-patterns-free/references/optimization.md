# Optimization Patterns

Section: Optimization Patterns

Source chapters: book/object-pool.markdown, book/flyweight.markdown, book/dirty-flag.markdown, book/spatial-partition.markdown, book/data-locality.markdown (structure only, prose omitted).
MIT code: code/cpp/object-pool.h, code/cpp/flyweight.h, code/cpp/dirty-flag.h, code/cpp/spatial-partition.h, code/cpp/data-locality.h (full file plus per-marker blocks in Sample Code).
Source repo: https://github.com/munificent/game-programming-patterns (MIT code only).
Licence: MIT code is free to reuse; chapter prose is NonCommercial, never sold, not included.

## Contents

## What is in this domain
## Sample Code

Section map: Dirty Flag, Object Pool, Spatial Partition, Data Locality sit under Optimization Patterns (patterns.md map). Flyweight also sits here: share what repeats.

## 4. Object Pool (code/cpp/object-pool.h)

Reuse fixed slots, never news per frame. ParticlePool holds Particle particles_[POOL_SIZE] plus firstAvailable_.
create(x, y, xVel, yVel, lifetime) takes the head of the free list; animate() steps live particles and pushes dead ones back with setNext(firstAvailable_).
Particle hides inUse_ and next; only the pool touches them.
Use when spawn rate is high (particles, bullets). Fixed size caps memory; init() returns false when full.

### Sample Code object-pool

```cpp
Particle particles_[POOL_SIZE];
Particle* firstAvailable_;
void ParticlePool::create(double x, double y, double xVel, double yVel, int lifetime) {
  Particle* p = firstAvailable_;
  firstAvailable_ = p->getNext();
  p->init(x, y, xVel, yVel, lifetime);
}
void ParticlePool::animate() {
  for (int i = 0; i < POOL_SIZE; i++) {
    if (particles_[i].animate()) {
      particles_[i].setNext(firstAvailable_);
      firstAvailable_ = &particles_[i];
    }
  }
}
```

## 13. Flyweight (code/cpp/flyweight.h)

Share what repeats. One Texture, Mesh, or Breed object serves hundreds of units; each unit keeps only x, y, health_.
Use when instance count explodes. Split shared (intrinsic) from per-unit (extrinsic) data.

### Sample Code flyweight

```cpp
class Texture {};
class Mesh {};
int x_;
int y_;
int health_;
```

## 14. Dirty Flag (code/cpp/dirty-flag.h)

Skip work that did not change. GraphNode::render(Transform parentWorld) combines local_ with parent only when the dirty flag is set, caches world, clears the flag; children reuse the cached world.
Use for scene graphs and derived data. Set the flag on every write path or stale data ships.

### Sample Code dirty-flag

```cpp
void GraphNode::render(Transform parentWorld) {
  Transform world = local_.combine(parentWorld);
  if (mesh_) renderMesh(mesh_, world);
  for (int i = 0; i < numChildren_; i++) children_[i]->render(world);
}
```

## 15. Spatial Partition (code/cpp/spatial-partition.h)

Only test neighbors. Grid with CELL_SIZE 20 and cells_[x][y]; add(unit), move(unit, x, y), findAt(x, y). handleMelee() walks each cell and calls handleCell, which calls handleUnit only on units in that cell.
Use when N units would otherwise need N-squared checks. Keep cell size near the melee range.

### Sample Code spatial-partition

```cpp
static const int CELL_SIZE = 20;
void Grid::add(Unit* unit) {}
void Grid::move(Unit* unit, double x, double y) {}
Unit* Grid::findAt(double x, double y) { return 0; }
void Grid::handleMelee() {}
void Grid::handleCell(int x, int y) {}
void handleUnit(Unit* a, Unit* b) {}
```

## 16. Data Locality (code/cpp/data-locality.h)

Keep hot data together. Thing things[NUM_THINGS] stepped in one for loop with doStuff(); cold fields split into a separate array so the hot loop stays in cache.
Use when the profiler names update loops. Pack, do not pad, the hot struct.

### Sample Code data-locality

```cpp
struct Thing { void doStuff() {} };
static const int NUM_THINGS = 3;
Thing things[NUM_THINGS];
for (int i = 0; i < NUM_THINGS; i++) things[i].doStuff();
```

## License

Code blocks above are MIT (Robert Nystrom, code/cpp/*.h).
Chapter prose is CC BY-NC-ND 4.0, NonCommercial, never sold, not included.
