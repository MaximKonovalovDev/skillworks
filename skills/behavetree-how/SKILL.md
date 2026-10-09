---
name: behavetree-how
description: Use when writing or fixing a BehaviorTree.CPP tree: node types, XML shape, tick returns, and halt rules with a checker that validates the file.
license: MIT
---

# behavetree-how

BehaviorTree.CPP in own words, plus a headless checker. The checker reads one tree XML file and answers `OK` or `ERROR` as the first word of stdout, with no network and no prompts.

## Use it

Run `scripts/behavetree_how.py` from this skill's folder, or give its full path:

```powershell
python scripts/behavetree_how.py --input <path> --out <path>
```

The first word of stdout is the answer:

- `OK 4 nodes MainTree`: exit 0. It wrote the tree ids and the node count to the `--out` file, one per line.
- `ERROR ...`: exit 2, nothing written. The causes, one clause each: missing input file, bad XML, refused path.

## Node types

BehaviorTree.CPP names five node types in `basic_types.h`: `ACTION`, `CONDITION`, `CONTROL`, `DECORATOR`, `SUBTREE`. Each custom C++ class reports one of them from `type()`.

- `ACTION` does work and may take time: it can answer `RUNNING` and must implement `halt()`. A `SyncActionNode` never answers `RUNNING`, and its `halt()` only resets the status.
- `CONDITION` asks a yes-or-no question about the world: it answers `SUCCESS` or `FAILURE`, never `RUNNING`, and must not change the world (no side-effects).
- `CONTROL` owns many children and picks which child to tick next. `Sequence` ticks children in order and stops at the first `FAILURE` or `RUNNING`. `Fallback` ticks children in order and stops at the first `SUCCESS` or `RUNNING`. `Parallel` ticks every child together. `ReactiveSequence` and `ReactiveFallback` restart at the first child on each tick, so an earlier child can preempt a `RUNNING` later child.
- `DECORATOR` owns exactly one child and changes what the child result means. `Inverter` swaps `SUCCESS` with `FAILURE`. `ForceSuccess` and `ForceFailure` replace the child result. `Repeat` and `Retry` tick the child again up to a count. `Timeout` stops a child that runs too long.
- `SUBTREE` reuses a tree by name: `<SubTree ID="Door"/>` runs the `BehaviorTree` whose `ID` is `Door`, with ports remapped at the call site.

The one-page reminder is `references/cheatsheet.md`.

## XML

A tree file opens with `<root BTCPP_format="4">` and holds one or more `<BehaviorTree ID="MainTree">` blocks. Each block nests control, decorator, and leaf tags. A custom leaf uses its registered C++ name as the tag, such as `<CheckBattery name="battery_ok"/>`.

- The root tag must be `root` and must carry `BTCPP_format` with the value `4`.
- Each `BehaviorTree` block needs a non-empty `ID`; the entry tree is named `MainTree` by convention.
- Each `SubTree` tag needs an `ID` that names a `BehaviorTree` block in the same file.
- Register each custom tag in C++ before loading, with `factory.registerNodeType` or a plugin, else the load fails.
- The Groot2 editor reads and writes the same XML, so the file stays hand-editable.

## Tick

To run a tree, tick it: `tree.tickWhileRunning()` ticks the root until it stops answering `RUNNING`. Each tick returns one status: `IDLE`, `RUNNING`, `SUCCESS`, `FAILURE`, or `SKIPPED`. A custom node never returns `IDLE`.

- A finished `ACTION` keeps `SUCCESS` or `FAILURE` until reset; it is not ticked again first.
- A `Sequence` answers `SUCCESS` only when every child answers `SUCCESS`.
- A `Fallback` answers `FAILURE` only when every child answers `FAILURE`.
- A `SequenceWithMemory` skips children that already answered `SUCCESS`; a `ReactiveSequence` re-ticks them on every tick.
- The pre-checks `_failureIf`, `_successIf`, and `_skipIf` run once when the node leaves `IDLE`; only `_while` can stop a `RUNNING` node, answering `SKIPPED`.

## Halt

`halt()` stops a `RUNNING` node and returns it to `IDLE`. A control node halts its `RUNNING` children first with `haltChildren()`. A decorator halts its single child with `haltChild()`. An async action stops its own work, such as a motor goal, before it resets.

- Never strand a `RUNNING` action without a `halt()` path: changing branches must stop the old branch.
- `SyncActionNode` and `ConditionNode` need no custom `halt()`; the base version only resets the status.
- After `halt()`, the next tick starts the node fresh from `IDLE`.

## Files

- `references/cheatsheet.md`: the one-page reminder of types, XML, tick, and halt.
- `references/sources.md`: upstream URLs, the MIT licence, the pin, and the files read.
