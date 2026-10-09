# Sources

Skill text and checker written fresh from the headers and examples below. No book PDF read, no text copied; only short node and call names are quoted.

- Origin: https://github.com/BehaviorTree/BehaviorTree.CPP (this skill: `skills/behavetree-how/`).
- Licence: MIT. Verified 2026-10-08: the repo LICENSE file carries the MIT text, and `gh api repos/BehaviorTree/BehaviorTree.CPP` answers licence `MIT` on branch `master`.
- Pin: commit `6a3b33702f3c50179f752d61b1aac99ac78199ea` on `master` (pushed 2026-10-03), read 2026-10-08 from a local `git clone --depth 1` (never committed).
- Files used: `include/behaviortree_cpp/basic_types.h` (NodeType, NodeStatus), `include/behaviortree_cpp/tree_node.h` (tick, halt, pre-checks), `include/behaviortree_cpp/control_node.h` (haltChildren), `include/behaviortree_cpp/decorator_node.h` (one child, haltChild), `include/behaviortree_cpp/action_node.h` (SyncActionNode, halt rules), `include/behaviortree_cpp/condition_node.h` (no RUNNING, no side-effects), `include/behaviortree_cpp/behavior_tree.h` (node list), `examples/t01_build_your_first_tree.cpp` (XML shape, tickWhileRunning), `examples/t04_reactive_sequence.cpp` (ReactiveSequence), `README.md` (MIT licence, XML loaded at run-time).
- Idea: behavior trees for robotics and games - control, decorator, and leaf nodes ticked to SUCCESS, FAILURE, or RUNNING, stopped with halt. Written from scratch in `scripts/behavetree_how.py`.
- Every statement in `SKILL.md` is run against the real script by `tests/test_behavetree_how.py`.

Credit line for THIRD_PARTY_NOTICES.md (only if promoted to fleet): BehaviorTree/BehaviorTree.CPP docs (MIT, pinned 6a3b337 read 2026-10-08; own words and own examples, short names only).
