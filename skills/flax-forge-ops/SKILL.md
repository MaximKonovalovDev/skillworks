---
name: flax-forge-ops
description: Operate the Forge AI game factory and Flax MCP bridge: gateway lanes, batch queues, MCP proxy, build and verify lanes. Use when working with Forge gateway, Flax tools, or factory sidecars.
version: 0.1.0
license: MIT
---

# Forge operations skill

Seed skill built from your own Forge docs. Start with
`references/lanes.md`, then the topic file you need.

## Use it

Run `scripts/flax_forge_ops.py` from this skill folder, or give its full path:

```powershell
python scripts/flax_forge_ops.py --input <path> --out <path>
python scripts/flax_forge_ops.py --help
```

The first word of stdout is the answer. The script prints:

- `RUN <n> lanes checked`: exit 0. It writes `report.json` in `--out` with the lanes checked.
- `ERROR ...`: exit 2, nothing written. Causes: missing input, input is not UTF-8, input is not JSON, bad plan, `--out` is a file, `--out` is the input path.

## Lanes

Chat, vision, embed, image, 3D, audio, music, TTS, STT and world run
through one OpenAI-compatible gateway with fallback chains. Batch work is
claimed with leases and requeued when stuck. The MCP proxy caps advertised
tools and discovers lazily. Failing calls refuse loudly with a recovery
hint instead of silent wrong output.

## Rules

- Gateway lanes carry one kind each with a fallback chain; a lane without its key refuses loudly and never fakes bytes.
- Batch work is claimed with a lease and requeued when stuck; never run the same batch twice without a fresh claim.
- The MCP proxy caps advertised tools and discovers lazily; a failing call prints `ERROR` with a recovery hint, exit 2.

Lane kinds, fallbacks and refusal lines: `references/lanes.md`.
