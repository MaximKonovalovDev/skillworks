# Sources

- Origin: https://github.com/ValveSoftware/GameNetworkingSockets (this skill's idea source, `skills/netcode-patterns/`).
- Licence: BSD-3-Clause. verified 2026-10-08: the repository LICENSE file holds the BSD-3-Clause licence text.
- Idea: connection states, send flags and P2P vocab from the GameNetworkingSockets docs, retold in own words. Written from scratch in `scripts/netcode_patterns.py`.
- Gambetta note: prediction, reconciliation, interpolation and lag compensation are ideas-only here, retold in own words; no text copied from the Gambetta pages.
- Every statement in `SKILL.md` is run against the real script by `tests/test_netcode_patterns.py`.
