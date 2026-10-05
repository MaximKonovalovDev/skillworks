---
name: flax-forge-ops
description: Operate the Forge AI game factory and Flax MCP bridge: gateway lanes, batch queues, MCP proxy, build and verify lanes. Use when working with Forge gateway, Flax tools, or factory sidecars.
version: 0.1.0
license: MIT
---

# Forge operations skill

Seed skill built from your own Forge docs. Start with
`references/lanes.md`, then the topic file you need.

## Lanes

Chat, vision, embed, image, 3D, audio, music, TTS, STT and world run
through one OpenAI-compatible gateway with fallback chains. Batch work is
claimed with leases and requeued when stuck. The MCP proxy caps advertised
tools and discovers lazily. Failing calls refuse loudly with a recovery
hint instead of silent wrong output.
