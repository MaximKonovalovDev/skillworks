# SHOP_PROOF: Fleet Vol 1, $19, v1.0.0

Pack: `fleet-vol-1` (3 paid skills + free Vol 0 `git-one-branch`).
Gate: `python tools/vol1_stranger_check.py` (replays pack_check at clean HEAD).
Date: 2026-10-05. Status: gate legs all PASS except clean-HEAD on this tree (see 1).

## 1. Stranger run (about 15 min)

Steps a stranger follows. Done here unless marked OPEN.

1. Clone the repo at this commit, `git status` clean. (Fails on this tree:
   6 untracked `tools/` files from other seats' in-flight work, plus this
   proof's own 2 new files pre-commit. packs/ and skills/ are clean.
   At a fresh clone this leg passes by construction.)
2. `python tools/pack_check.py packs/fleet-vol-1` -> must print RESULT PASS.
3. `python tools/vol1_stranger_check.py` -> clean HEAD, pack_check replay,
   vol0 free, price agrees, 3 pages. All legs PASS here except leg 1.
4. Unzip `dist/fleet-vol-1-vol0.zip`, copy the skill, ask the agent which
   skills it has. OPEN: needs a human outside the loop (listing.md says so).
5. Buy path: Gumroad live page (listing.md Live listing line), $19 once.
   Install `fleet-vol-1.zip` per README-buyer.md, check `manifest.json`
   sha256, check one `zips/<name>.zip` loads. OPEN: needs a real buyer.

## 2. Eyes vs reference

A human opened every listing-named asset 2026-10-05. All render, all match.

| File | Bytes | Magic | Listing says |
|---|---|---|---|
| store-art/O-025/out.png | 319491 | PNG | cover 1280x720 |
| store-art/O-025/out-630x500.png | 131799 | PNG | itch card |
| store-art/O-033/demo.gif | 167382 | GIF | 480x288 15 s 167382 B |
| store-art/O-033/out.png | 283421 | PNG | demo poster 1280x720 |
| store-art/O-033/out-630x500.png | 134298 | PNG | demo card |
| store-art/shots/shot-pairs.png | 64153 | PNG | pairs table capture |
| store-art/shots/shot-wd.png | 27523 | PNG | webdriver JSON capture |
| store-art/shots/shot-bevy.png | 61620 | PNG | bevy table capture |

## 3. Dogfood (a loop uses the skill)

- `pwsh-for-bash-writers`: 29 loads in 48 h across the fleet (board DR-1005-1,
  scan 2026-10-05). The paid skill runs in real loops today.
- `real-browser-automation`: 5 loads in 24 h (board DR-1004-8).
- Forge-loop session proof (one pinned forge session loading a Vol 1 skill):
  OPEN, not claimed. No forge file names any Vol 1 skill (checked 2026-10-05).

## 4. GIF gap (named)

`demo/demo.gif`: the old 43-byte 1-pixel stub flagged by the 2026-10-03 audit.
It is gone (path no longer exists). The listing's demo is the real capture
`store-art/O-033/demo.gif` (167382 B, 480x288, 15 s, order O-033). One honest
gap stays: the brief asked 10 s at 1280x720, the render gate makes 480x288,
so the listing says 15 s 480x288, not 1280x720.

## 5. UNKNOWN views = FAIL

Sales stays 0 until a store payout or report names a buyer. Views, drafts and
unknowns never count. Any UNKNOWN in the sales line fails this proof.
Re-run the gate before claiming a sale.

## Proof (2026-10-05)

- `python tools/pack_check.py packs/fleet-vol-1` -> RESULT PASS
  (13 checks pass, 0 warnings, 0 store assets still needed).
- `python tools/vol1_stranger_check.py` -> all legs PASS except clean-HEAD
  on this tree (other seats' 6 untracked tools/ files, named in section 1).
- `pytest tests/test_pack_check.py -q` -> 34 passed, 1 skipped.
- `node sprint/check.mjs` -> RESULT PASS (20 pass, 0 warn, 0 fail).
