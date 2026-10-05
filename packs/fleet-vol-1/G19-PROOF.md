# G-19 proof: Vol 1 badges + stranger video script

Pack: `fleet-vol-1` ($19, v1.0.0). Date: 2026-10-05.
Tool: `tools/g19-badge.py` (read-only, no writes, no network).
This file is proof only. It changes no pack file, no board, no handoff.

## Badges

Two lines. Installs links the live Vol 1 page. Official links the repo.
Counts stay honest: installs 0, sales 0, until a real sale. Views never count.

[![installs](https://img.shields.io/badge/installs-0-blue)](https://maxkonova.gumroad.com/l/fleet-pack)
[![official](https://img.shields.io/badge/source-official-green)](https://github.com/MaximKonovalovDev/skillworks)

Source of truth: `python tools/g19-badge.py --badges` prints the same two lines.

## Stranger 15-min video script (teach style)

Source of truth: `python tools/g19-badge.py --script` prints this script.

Stranger 15-min run (teach style, one PC, PowerShell 7).

You teach one habit. You link Vol 1 once, at the end. You measure one click.

0-2 min (hook, one fail):
- Open PowerShell 7. Make notes.txt with 5 lines.
- Type: head -n 2 notes.txt
- Show the red error: head is not recognized. Say: this is the mistake agents make daily.

2-10 min (teach, three pairs):
- Pair 1: Get-Content -TotalCount 2 notes.txt (first two lines).
- Pair 2: Select-String -Pattern word notes.txt (search, not grep).
- Pair 3: @(Get-Content notes.txt).Count (count lines, not wc).
- Each pair: bash form fails or lies, pwsh form prints the answer. Let the stranger type all three.

10-13 min (prove it is tested):
- Say: these three come from a tested skill with 49 such pairs, each run in PowerShell 7.
- Run one proof line the stranger can redo: ask the agent for the first two lines without saying how, watch it use Get-Content.

13-15 min (link Vol 1 once + measure):
- Say: this habit plus 48 more, a real-browser skill and a Bevy skill are Fleet Vol 1, $19 once: https://maxkonova.gumroad.com/l/fleet-pack
- Free sample first: the Vol 0 git skill is free and never sold.
- Measure: ask the stranger to say OPENED (link opened) or SKIPPED. Record one of the two words plus the date. That is the click-through count.
- Rule: views and drafts never count. Sales stay 0 until a store payout or report names a buyer.

## Click-through measure

One run = one line: date plus OPENED or SKIPPED. No runs yet.

| Date | Stranger | Result |
|---|---|---|
| - | none yet | - |

## Proof runs (2026-10-05)

- `python tools/g19-badge.py --check` -> RESULT PASS (12 PASS, 0 FAIL).
- `python tools/pack_check.py packs/fleet-vol-1` -> RESULT PASS (13 checks pass, 0 warnings, 0 still needed).
- `node sprint/check.mjs` -> RESULT PASS (20 pass, 0 warn, 0 fail).

Pack files unchanged: only these two new files added
(`packs/fleet-vol-1/G19-PROOF.md`, `tools/g19-badge.py`).
