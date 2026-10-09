# behavetree-how cheatsheet

Five node types: `ACTION` (may answer `RUNNING`, needs `halt()`), `CONDITION` (`SUCCESS` or `FAILURE` only, no side-effects), `CONTROL` (`Sequence`, `Fallback`, `Parallel`, `ReactiveSequence`, `ReactiveFallback`), `DECORATOR` (exactly one child: `Inverter`, `ForceSuccess`, `ForceFailure`, `Repeat`, `Retry`, `Timeout`), `SUBTREE` (a `SubTree` tag whose `ID` names a `BehaviorTree` block).

XML: the root tag is `root` with `BTCPP_format="4"`. Each `BehaviorTree` block needs an `ID`; the entry tree is `MainTree`. Register each custom tag with `factory.registerNodeType` or a plugin before loading.

Tick: `tree.tickWhileRunning()` ticks until the root stops answering `RUNNING`. Statuses: `IDLE`, `RUNNING`, `SUCCESS`, `FAILURE`, `SKIPPED`. A custom node never returns `IDLE`. `Sequence` stops at the first `FAILURE` or `RUNNING`; `Fallback` stops at the first `SUCCESS` or `RUNNING`. A finished `ACTION` keeps its result until reset.

Halt: `halt()` returns a node to `IDLE`. Controls call `haltChildren()`; decorators call `haltChild()`; async actions stop their own work first. `SyncActionNode` and `ConditionNode` only reset.

Checker: `python scripts/behavetree_how.py --input <path> --out <path>` prints `OK <n> nodes <ids>` with exit 0 and writes the `--out` file, or `ERROR ...` with exit 2 and nothing written.
