## 0000
# file: acknowledgements.md

# Acknowledge&shy;ments

Source chapter: book/acknowledgements.markdown (structure only, prose omitted).

## License

Code blocks above are MIT (Robert Nystrom, code/cpp/*.h).
Chapter prose is CC BY-NC-ND 4.0, NonCommercial, never sold, not included.

# file: architecture-performance-and-games.md

# Architecture, Performance, and Games

Section: Introduction

Source chapter: book/architecture-performance-and-games.markdown (structure only, prose omitted).

## Contents

## What is Software Architecture?
### What is *good* software architecture?
### How do you make a

## 0001
ME);
        break;
        //^omit
      case INST_LITERAL:
      case INST_GET_HEALTH:
      case INST_GET_WISDOM:
      case INST_GET_AGILITY:
      case INST_ADD:
        break;
        //^omit
    }
    //^interpret-instruction
  }

  namespace NoParams
  {
  //^vm
  class VM
  {
  public:
    void interpret(char bytecode[], int size)
    {
      for (int i = 0; i < size; i++)
      {
        char instruction = bytecode[i];
        switch (instruction)
        {
          // Cases for each instruction...
            //^omit
          case INST_SPAWN_PARTICLES:
            break;
         

## 0002
tton button) { return false; }
  void jump() {}
  void fireGun() {}
  void swapWeapon() {}
  void lurchIneffectively() {}

  namespace BeforeCommand
  {
    class InputHandler
    {
    public:
      void handleInput();
    };

    //^handle-input
    void InputHandler::handleInput()
    {
      if (isPressed(BUTTON_X)) jump();
      else if (isPressed(BUTTON_Y)) fireGun();
      else if (isPressed(BUTTON_A)) swapWeapon();
      else if (isPressed(BUTTON_B)) lurchIneffectively();
    }
    //^handle-input
  }

  namespace InputHandlingCommand
  {
    //^command
    class Command
    {
    publ

## 0003
         yBefore_ = unit_->y();

          unit_->moveTo(x_, y_);
        }

        virtual void undo()
        {
          unit_->moveTo(xBefore_, yBefore_);
        }

      private:
        Unit* unit_;
        int xBefore_, yBefore_;
        int x_, y_;
      };
      //^undo-move-unit
    }
  }
}

#endif
```

## License

Code blocks above are MIT (Robert Nystrom, code/cpp/*.h).
Chapter prose is CC BY-NC-ND 4.0, NonCommercial, never sold, not included.

# file: component.md

# Component

Section: Decoupling Patterns

Source chapter: book/component.markdown (structure only, prose omitted).

## 0004
;

    Bjorn(InputComponent* input)
    : input_(input)
    {}

    void update(World& world, Graphics& graphics)
    {
      input_->update(*this);
      physics_.update(*this, world);
      graphics_.update(*this, graphics);
    }

  private:
    InputComponent* input_;
    PhysicsComponent physics_;
    GraphicsComponent graphics_;
  };
  
```

### Code component part 11

```cpp

      Bjorn* bjorn = new Bjorn(new PlayerInputComponent());
      
```

### Code component part 12

```cpp

  class DemoInputComponent : public InputComponent
  {
  public:
    virtual void update(Bjorn& bjorn)
   

## 0005
)
    {
      case DIR_LEFT:
        velocity_ -= WALK_ACCELERATION;
        break;
      
      case DIR_RIGHT:
        velocity_ += WALK_ACCELERATION;
        break;
      //^omit
      case DIR_NONE: break; // Do nothing.
      //^omit
    }
    
    // Modify position by velocity.
    x_ += velocity_;
    world.resolveCollision(volume_, x_, y_, velocity_);
    
    // Draw the appropriate sprite.
    Sprite* sprite = &spriteStand_;
    if (velocity_ < 0)
    {
      sprite = &spriteWalkLeft_;
    }
    else if (velocity_ > 0)
    {
      sprite = &spriteWalkRight_;
    }
    
    graphics.

## 0006
  //^10
  class Bjorn
  {
  public:
    int velocity;
    int x, y;

    Bjorn(InputComponent* input)
    : input_(input)
    {}

    void update(World& world, Graphics& graphics)
    {
      input_->update(*this);
      physics_.update(*this, world);
      graphics_.update(*this, graphics);
    }

  private:
    InputComponent* input_;
    PhysicsComponent physics_;
    GraphicsComponent graphics_;
  };
  //^10

  //^12
  class DemoInputComponent : public InputComponent
  {
  public:
    virtual void update(Bjorn& bjorn)
    {
      // AI to automatically control Bjorn...
    }
  };
  //^12



## 0007
locality_h

// TODO(bob):
//
// cache effects are magnified by:
// - turning up number of actors
// - adding padding to the actor class
//   (both because it spaces the actors out more in memory)
//   in examples below, creating much bigger shuffled array just to spread
//   them out more.
// - adding padding to component magnifies it too, but also punishes best case

namespace DataLocality
{
  void sleepFor500Cycles() {}

  struct Thing
  {
    void doStuff() {}
  };

  static const int NUM_THINGS = 3;

  void callDoNothing()
  {
    Thing things[NUM_THINGS];

    //^do-nothing
    for (int i

## 0008
   // right after the active ones.
    Particle temp = particles_[numActive_];
    particles_[numActive_] = particles_[index];
    particles_[index] = temp;

    // Now there's one more.
    numActive_++;
  }
  //^activate-particle

  //^deactivate-particle
  void ParticleSystem::deactivateParticle(int index)
  {
    // Shouldn't already be inactive!
    assert(index < numActive_);

    // There's one fewer.
    numActive_--;

    // Swap it with the last active particle
    // right before the inactive ones.
    Particle temp = particles_[numActive_];
    particles_[numActive_] = particles_[i

## 0009
_;
      Mesh* mesh_;

      GraphNode* children_[MAX_CHILDREN];
      int numChildren_;
    };

    //^render-on-fly
    void GraphNode::render(Transform parentWorld)
    {
      Transform world = local_.combine(parentWorld);

      if (mesh_) renderMesh(mesh_, world);

      for (int i = 0; i < numChildren_; i++)
      {
        children_[i]->render(world);
      }
    }
    //^render-on-fly

    void root()
    {
      GraphNode* graph_ = new GraphNode(NULL);
      //^render-root
      graph_->render(Transform::origin());
      //^render-root
    }
  }

  namespace Dirty
  {
    //^dirty-gr

## 0010
tors_[i]->reset();
      }
    }

  private:
    static const int NUM_ACTORS = 3;

    Actor* actors_[NUM_ACTORS];
  };
  
```

### Code double-buffer part 7

```cpp

  class Comedian : public Actor
  {
  public:
    //^omit
    Comedian() : name_("") {}
    Comedian(const char* name) : name_(name) {}
    //^omit
    void face(Actor* actor) { facing_ = actor; }

    virtual void update()
    {
      //^omit
      if (wasSlapped()) std::cout << name_ << " was slapped" << std::endl;
      //^omit
      if (wasSlapped()) facing_->slap();
    }

  private:
    //^omit
    const char* name_;
    //

## 0011

    Comedian() : name_("") {}
    Comedian(const char* name) : name_(name) {}
    //^omit
    void face(Actor* actor) { facing_ = actor; }

    virtual void update()
    {
      //^omit
      if (wasSlapped()) std::cout << name_ << " was slapped" << std::endl;
      //^omit
      if (wasSlapped()) facing_->slap();
    }

  private:
    //^omit
    const char* name_;
    //^omit
    Actor* facing_;
  };
  //^7

  void sample1()
  {
    //^8
    Stage stage;

    Comedian* harry = new Comedian();
    Comedian* baldy = new Comedian();
    Comedian* chump = new Comedian();

    harry->face(baldy)

## 0012
(SoundId id) { return 0; }
  int findOpenChannel() { return -1; }
  void startSound(ResourceId resource, int channel, int volume) {}

  namespace EventLoop
  {
    typedef int Event;
    Event getNextEvent() { return 0; }

    void eventLoop()
    {
      bool running = true;
      //^event-loop
      while (running)
      {
        Event event = getNextEvent();
        // Handle event...
        //^omit
        use(event);
        //^omit
      }
      //^event-loop
    }
  }

  namespace Unqueued
  {
    //^sync-api
    class Audio
    {
    public:
      static void playSound(SoundId id, in

## 0013
= -1) return;
      startSound(resource, channel, pending_[head_].volume);

      head_ = (head_ + 1) % MAX_PENDING;
    }
    //^ring-update

    PlayMessage Audio::pending_[MAX_PENDING];
    int Audio::tail_;
    int Audio::head_;
  }

  namespace Duplicate
  {
    class Audio
    {
    public:
      static void init()
      {
        head_ = 0;
        tail_ = 0;
      }

      static void playSound(SoundId id, int volume);
      static void update();
    private:
      static const int MAX_PENDING = 16;

      static PlayMessage pending_[MAX_PENDING];
      static int head_;
      static i

## 0014
  return 3;
        case TERRAIN_RIVER: return 2;
          // Other terrains...
      }
    }

    bool World::isWater(int x, int y)
    {
      switch (tiles_[x][y])
      {
        case TERRAIN_GRASS: return false;
        case TERRAIN_HILL:  return false;
        case TERRAIN_RIVER: return true;
          // Other terrains...
      }
    }
    //^enum-data
  }

  namespace TerrainClass
  {
    //^terrain-class
    class Terrain
    {
    public:
      Terrain(int movementCost,
              bool isWater,
              Texture texture)
      : movementCost_(movementCost),
        isWater_(i

## 0015
= getCurrentTime();
      processInput();
      update();
      render();

      sleep(start + MS_PER_FRAME - getCurrentTime());
    }
    
```

### Code game-loop part 5

```cpp

    double lastTime = getCurrentTime();
    while (true)
    {
      double current = getCurrentTime();
      double elapsed = current - lastTime;
      processInput();
      update(elapsed);
      render();
      lastTime = current;
    }
    
```

### Code game-loop part 6

```cpp

    double previous = getCurrentTime();
    double lag = 0.0;
    while (true)
    {
      double current = getCurrentTime();
      dou

## 0016
 prose omitted).
MIT code: code/cpp/introduction.h (full file below, plus per-marker blocks).

## Contents

## What's in Store
## How it Relates to Design Patterns
## How to Read the Book
## About the Sample Code
## Where to Go From Here

### Full MIT source code/cpp/introduction.h

```cpp
//
//  introduction.h
//  cpp
//
//  Created by Bob Nystrom on 8/19/13.
//  Copyright (c) 2013 Bob Nystrom. All rights reserved.
//

#ifndef cpp_introduction_h
#define cpp_introduction_h

//^update
bool update()
{
  // Do work...
  return isDone();
}
//^update

#endif
```

## License

Code blocks above are M

## 0017
Vel, yVel, lifetime);
  }
  
```

### Code object-pool part 8

```cpp

  void ParticlePool::animate()
  {
    for (int i = 0; i < POOL_SIZE; i++)
    {
      if (particles_[i].animate())
      {
        // Add this particle to the front of the list.
        particles_[i].setNext(firstAvailable_);
        firstAvailable_ = &particles_[i];
      }
    }
  }
  
```

### Code object-pool part 10

```cpp

  class Particle
  {
    friend class ParticlePool;

  private:
    Particle()
    : inUse_(false)
    {}

    bool inUse_;
  };

  class ParticlePool
  {
    Particle pool_[100];
  };
  
```

###

## 0018
articles_[POOL_SIZE];
    //^omit
    Particle* firstAvailable_;
  };
  //^5

  //^6
  ParticlePool::ParticlePool()
  {
    // The first one is available.
    firstAvailable_ = &particles_[0];

    // Each particle points to the next.
    for (int i = 0; i < POOL_SIZE - 1; i++)
    {
      particles_[i].setNext(&particles_[i + 1]);
    }

    // The last one terminates the list.
    particles_[POOL_SIZE - 1].setNext(NULL);
  }
  //^6

  //^7
  void ParticlePool::create(double x, double y,
                            double xVel, double yVel,
                            int lifetime)
  {
    //

## 0019
t event) {}
    };

    //^physics-update
    void Physics::updateEntity(Entity& entity)
    {
      bool wasOnSurface = entity.isOnSurface();
      entity.accelerate(GRAVITY);
      entity.update();
      if (wasOnSurface && !entity.isOnSurface())
      {
        notify(entity, EVENT_START_FALL);
      }
    }
    //^physics-update
  }

  namespace Pattern
  {
    //^observer
    class Observer
    {
    public:
      virtual ~Observer() {}
      virtual void onNotify(const Entity& entity, Event event) = 0;
    };
    //^observer

    //^achievement-observer
    class Achievements : public Ob

## 0020

    //^linked-notify
  }

  namespace One
  {
    class Observable;

    class Observer
    {
      friend class Observable;

    public:
      bool isObserving() const { return observable_ != NULL; }

      void observe(Observable& observable);
      void detach();

    protected:
      Observer()
      : prev_(this),
        next_(this)
      {}

      virtual ~Observer()
      {
        detach();
      }

      virtual void onNotify(Observable& observable) = 0;

    private:
      // The Observable this Observer is watching.
      Observable* observable_ = NULL;

      // The next and prev

## 0021
T(ear3.numObserved == 1);

      ear2.detach();
      noise1.sound();
      ASSERT(ear1.numObserved == 4);
      ASSERT(ear2.numObserved == 2);
      ASSERT(ear3.numObserved == 2);

      ear1.detach();
      noise1.sound();
      ASSERT(ear1.numObserved == 4);
      ASSERT(ear2.numObserved == 2);
      ASSERT(ear3.numObserved == 3);

      ear3.detach();
      noise1.sound();
      ASSERT(ear1.numObserved == 4);
      ASSERT(ear2.numObserved == 2);
      ASSERT(ear3.numObserved == 3);
    }

    void observeTest()
    {
      Ear ear("ear");
      Noise beep("beep");
      Noise boop("boop");

## 0022
/^templates
    class Spawner
    {
    public:
      virtual ~Spawner() {}
      virtual Monster* spawnMonster() = 0;
    };

    template <class T>
    class SpawnerFor : public Spawner
    {
    public:
      virtual Monster* spawnMonster() { return new T(); }
    };
    //^templates

    void test()
    {
      //^use-templates
      Spawner* ghostSpawner = new SpawnerFor<Ghost>();
      //^use-templates
      use(ghostSpawner);
    }
  }
}

#endif
```

## License

Code blocks above are MIT (Robert Nystrom, code/cpp/*.h).
Chapter prose is CC BY-NC-ND 4.0, NonCommercial, never sold, not inc

## 0023
& getAudio()
    {
      Audio* service = NULL;

      // Code here to locate service...

      assert(service != NULL);
      return *service;
    }
  };
  
```

### Code service-locator part 3

```cpp

  class Base
  {
    // Code to locate service and set service_...

  protected:
    // Derived classes can use service
    static Audio& getAudio() { return *service_; }

  private:
    static Audio* service_;
  };
  
```

### Full MIT source code/cpp/service-locator.h

```cpp
#include <iostream>

class AudioSystem
{
public:
  static void playSound(int id) {}
  static AudioSystem* instance() 

## 0024
rose omitted).
MIT code: code/cpp/singleton.h (full file below, plus per-marker blocks).

## Contents

## The Singleton Pattern
### Restricting a class to one instance
### Providing a global point of access
## Why We Use It
## Why We Regret Using It
### It's a global variable
### It solves two problems even when you just have one
### Lazy initialization takes control away from you
## What We Can Do Instead
### See if you need the class at all
### To limit a class to a single instance
### To provide convenient access to an instance
## What's Left for Singleton

### Code singleton part 1

```cpp

## 0025
= new FileSystem();
      return *instance;
    }

  private:
    FileSystem() {}
  };
  //^local-static

  void test()
  {
    if (&FileSystem::instance() == NULL)
    {
      std::cout << "singleton is null!" << std::endl;
    }
    else
    {
      std::cout << "singleton is ok" << std::endl;
    }
  }
}

namespace Singleton2
{
  //^2
  class FileSystem
  {
  public:
    virtual ~FileSystem() {}
    virtual char* readFile(char* path) = 0;
    virtual void  writeFile(char* path, char* contents) = 0;
  };
  //^2
  
  //^derived-file-systems
  class PS3FileSystem : public FileSystem
  {
  publ

## 0026
ance_ = Game();

  void foo()
  {
    int VERY_LOUD_BANG = 0;
    //^12
    Game::instance().getAudioPlayer().play(VERY_LOUD_BANG);
    //^12
  }
}
```

## License

Code blocks above are MIT (Robert Nystrom, code/cpp/*.h).
Chapter prose is CC BY-NC-ND 4.0, NonCommercial, never sold, not included.

# file: spatial-partition.md

# Spatial Partition

Section: Optimization Patterns

Source chapter: book/spatial-partition.markdown (structure only, prose omitted).
MIT code: code/cpp/spatial-partition.h (full file below, plus per-marker blocks).

## Contents

## Intent
## Motivation
### Units on the 

## 0027
     }
    }
    //^add
  }

  namespace FixedGrid
  {
    class Unit;

    void handleAttack(Unit* unit, Unit* other)
    {

    }
    
    class Grid
    {
    public:
      Grid()
      {
        // Clear the grid.
        for (int x = 0; x < NUM_CELLS; x++)
        {
          for (int y = 0; y < NUM_CELLS; y++)
          {
            cells_[x][y] = NULL;
          }
        }
      }

      static const int CELL_SIZE = 20;

      void move(Unit* unit, double x, double y);
      void add(Unit* unit);

      Unit* findAt(double x, double y);

      void handleMelee();
      void handleCell

## 0028
ttack(Unit* unit, Unit* other)
    {

    }

    int distance(Unit* a, Unit* b) { return 3; }

    class Grid
    {
    public:
      Grid()
      {
        // Clear the grid.
        for (int x = 0; x < NUM_CELLS; x++)
        {
          for (int y = 0; y < NUM_CELLS; y++)
          {
            cells_[x][y] = NULL;
          }
        }
      }

      static const int CELL_SIZE = 20;

      void move(Unit* unit, double x, double y);
      void add(Unit* unit);

      Unit* findAt(double x, double y);

      void handleMelee();
      void handleCell(int x, int y);
      void handleUnit(Unit

## 0029
nput);
      double yVelocity_;
      bool isJumping_;
    };

    //^spaghetti-3
    void Heroine::handleInput(Input input)
    {
      if (input == PRESS_B)
      {
        // Jump if not jumping...
      }
      else if (input == PRESS_DOWN)
      {
        if (!isJumping_)
        {
          setGraphics(IMAGE_DUCK);
        }
      }
      else if (input == RELEASE_DOWN)
      {
        setGraphics(IMAGE_STAND);
      }
    }
    //^spaghetti-3
  }

  namespace Spaghetti4
  {
    class Heroine
    {
    public:
      void setGraphics(Animate animate) {}
      void handleInput(Input input)

## 0030
break;
          //^omit
      }
    }
    //^state-switch-reset
  }
  
  namespace StatePattern
  {
    class Heroine;
    class JumpingState;

    //^heroine-state
    class HeroineState
    {
    public:
      //^omit
      static JumpingState jumping;
      //^omit
      virtual ~HeroineState() {}
      virtual void handleInput(Heroine& heroine, Input input) {}
      virtual void update(Heroine& heroine) {}
    };
    //^heroine-state

    class JumpingState : public HeroineState {};
    
    class StandingState;

    //^gof-heroine
    class Heroine
    {
      //^omit
      friend class 

## 0031
HeroineState
    {
    public:
      virtual ~HeroineState() {}
      virtual void enter(Heroine& heroine) {}
      virtual HeroineState* handleInput(Heroine& heroine, Input input)
      {
        return NULL;
      }
    };

    class Heroine
    {
    public:
      void handleInput(Input input);
      void setGraphics(Animate animate) {}
    private:
     
```

## License

Code blocks above are MIT (Robert Nystrom, code/cpp/*.h).
Chapter prose is CC BY-NC-ND 4.0, NonCommercial, never sold, not included.

# file: subclass-sandbox.md

# Subclass Sandbox

Section: Behavioral Patterns

Source ch

## 0032


```cpp

  class Superpower
  {
  protected:
    void spawnParticles(ParticleType type, int count)
    {
      ParticleSystem& particles = Locator::getParticles();
      particles.spawn(type, count);
    }

    // Sandbox method and other operations...
  };
  
```

### Full MIT source code/cpp/subclass-sandbox.h

```cpp
typedef int SoundId;
typedef int ParticleType;

const SoundId SOUND_SPROING = 1;
const SoundId SOUND_SWOOP = 1;
const SoundId SOUND_DIVE = 1;
const ParticleType PARTICLE_DUST = 1;
const ParticleType PARTICLE_SPARKLES = 1;

namespace SimpleExample
{
  //^1
  class Superpower
  

## 0033
ticState
{
  class ParticleSystem {};

  //^11
  class Superpower
  {
  public:
    static void init(ParticleSystem* particles)
    {
      particles_ = particles;
    }

    // Sandbox method and other operations...

  private:
    static ParticleSystem* particles_;
  };
  //^11
}

namespace UseServiceLocator
{
  struct ParticleSystem
  {
    void spawn(ParticleType type, int count);
  };

  ParticleSystem particles;

  class Locator
  {
  public:
    static ParticleSystem& getParticles() { return particles; }
  };

  //^12
  class Superpower
  {
  protected:
    void spawnParticles(ParticleT

## 0034
eed_; }

    // Existing code...
    //^omit
    Breed& breed_;
    //^omit
  };
  
```

### Code type-object part 12

```cpp

  const char* Monster::getAttack()
  {
    if (health_ < LOW_HEALTH)
    {
      return "The monster flails weakly.";
    }

    return breed_.getAttack();
  }
  
```

### Full MIT source code/cpp/type-object.h

```cpp
#include "common.h"

namespace Subclasses
{
  //^1
  class Monster
  {
  public:
    virtual ~Monster() {}
    virtual const char* getAttack() = 0;

  protected:
    Monster(int startingHealth)
    : health_(startingHealth)
    {}

  private:
    int hea

## 0035
_;
  };

  #define LOW_HEALTH 1

  //^12
  const char* Monster::getAttack()
  {
    if (health_ < LOW_HEALTH)
    {
      return "The monster flails weakly.";
    }

    return breed_.getAttack();
  }
  //^12
}
```

## License

Code blocks above are MIT (Robert Nystrom, code/cpp/*.h).
Chapter prose is CC BY-NC-ND 4.0, NonCommercial, never sold, not included.

# file: update-method.md

# Update Method

Section: Sequencing Patterns

Source chapter: book/update-method.markdown (structure only, prose omitted).
MIT code: code/cpp/update-method.h (full file below, plus per-marker blocks).

## Conten

## 0036
ndering...
      }
    }
    //^game-loop

    //^skeleton
    class Skeleton : public Entity
    {
    public:
      Skeleton()
      : patrollingLeft_(false)
      {}

      virtual void update()
      {
        if (patrollingLeft_)
        {
          setX(x() - 1);
          if (x() == 0) patrollingLeft_ = false;
        }
        else
        {
          setX(x() + 1);
          if (x() == 100) patrollingLeft_ = true;
        }
      }

    private:
      bool patrollingLeft_;
    };
    //^skeleton

    //^statue
    class Statue : public Entity
    {
    public:
      Statue(int delay)
