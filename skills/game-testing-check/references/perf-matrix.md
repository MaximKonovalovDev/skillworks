# Perf matrix

Own-words checklist. No book text is copied.

| Check | What to do | Pass row |
|---|---|---|
| `stress testing` | simulate `multiple players` at once, download spikes, hotspot crowding | game stays up, no data loss, errors are counted |
| `load testing` | scripted load, can be `automated`, often with `backend developers` | limits named: users, rate, size before degrade |
| `frame rate` and `lag` | play a busy scene and watch `performance under stress` | `frame rate` steady, no `lag` or delay felt in input |
| `compatibility` | run on each target device and OS | same build passes on every target in the set |
| `installability` | install, update, remove, check size and file location | clean install, update, and clean removal |
| `test sets` | keep low, mid, high tiers ready | set covers tiers; this is `hardware compatibility` |
| `scalability` | add content and features on a live-like build | new content loads with no perf drop |

Rules:

- Name the rig: device, OS, build, network. Note `frame rate` numbers and any `lag` with time and place.
- File perf bugs with repro steps, count, and rig. Link the run log.

