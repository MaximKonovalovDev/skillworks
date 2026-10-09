---
name: netcode-patterns
description: Check a netcode message plan for send flags, connection states and P2P terms before it ships. Use when choosing GameNetworkingSockets send flags or reviewing a multiplayer message plan.
license: MIT
version: 0.1.0
author: skillworks
---

# netcode-patterns

Check a multiplayer message plan before it ships. Headless: no network, no prompts. It reads one plan file and checks send flags, connection states and P2P terms.

## Use it

Run `scripts/netcode_patterns.py` from this skill's folder, or give its full path:

```powershell
python scripts/netcode_patterns.py --input plan.json --out dir
```

`--input` is a plan.json file. `--out` is a folder that will hold report.json.

The first word of stdout is the answer:

- `RUN <n> messages flags <m> warnings <w>`: exit 0. It writes report.json in the --out folder with tool, messages, flags and warnings.
- `ERROR ...`: exit 2, nothing written. Causes: input file missing, input is not UTF-8, input is not JSON, bad plan with a reason, --out is a file, --out is the input file.

## Rules

- Plan shape: the top object holds a messages list. Each message has name, delivery, urgent, size and per_second. Name matches [a-z0-9_] with 1 to 32 chars and must be unique across the plan. Delivery is reliable or unreliable in lower case only. Urgent is a bool. Size is 1 to 524288. Per_second is over 0 and at most 120.
- Flag choice: reliable false and urgent false gives Unreliable. Reliable false and urgent true gives UnreliableNoNagle. Reliable true and urgent false gives Reliable. Reliable true and urgent true gives ReliableNoNagle. NoDelay sends at once with no wait. NoNagle skips wait and sends at once. Reliable resends until the peer acks. UseCurrentThread and AutoRestartBrokenSession off.
- States: None, Connecting, FindingRoute, Connected, ClosedByMe, ClosedByPeer, FinWait, Linger, ProblemDetectedLocally. Only Connected carries game traffic. Never send game input before Connected. Never send before Connected.
- P2P words: identity is who you are, listen socket takes new links, connection is one peer link, poll group reads many links at once, signaling swaps addresses, NAT traversal punches the path, relay carries packets when direct fails.
- Smooth play ideas: prediction guesses your next move at once, reconciliation fixes a wrong guess when the server truth lands, interpolation shows others a little in the past to keep motion smooth, lag compensation rewinds the world to check a late shot. Send repeated positions over Unreliable. Send scores and chat over Reliable.
- This tool does not open sockets, send packets, or join session; only checks plan and writes report.json.

Details, bits and guards: `references/patterns.md`.
