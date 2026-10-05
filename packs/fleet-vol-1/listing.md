# Fleet Vol 1: three tested skills for coding agents

Tagline: Three Agent Skills run against real programs: PowerShell 7, a real browser over CDP, Bevy 0.19.

Status: live on Gumroad since 2026-10-04 (the page answers HTTP 200); cover art delivered 2026-10-04 (order O-025, 1280x720 + 630x500 PNGs in store-art/O-025/), demo delivered 2026-10-04 (order O-033, GIF + poster + card in store-art/O-033/), screenshots delivered 2026-10-04 (three real 1280x800 captures in store-art/shots/).
Live listing: https://maxkonova.gumroad.com/l/fleet-pack
Price: $19
AI disclosure: generated: the text and scripts of the skills were written by AI coding agents (Claude); every example and claim was then run on real programs and checked by tests. No generated images in the pack.
Category: Tool
Tags: agent-skills, claude-code, opencode, powershell, bevy, devtools-protocol
Author: skillworks (the store account decides the display name)
Repository: https://github.com/MaximKonovalovDev/skillworks
Stars: 0 (not listed, no stars)
Weekly installs: 0 (not listed, no installs)
Sales: 0 (stays 0 until a real sale; views and drafts are not sales)

## What it is

Agent Skills are folders with a `SKILL.md` that a coding agent loads when the task matches. These three each fix a
mistake agents make again and again. Nothing in them is a prompt trick: the examples were run, the names were checked
against the source, and the results are in `proof/`.

## What is inside

Pack file `fleet-vol-1.zip`, version 1.0.0. Each skill is a folder in `skills/` and also its own zip in `zips/`.

| Skill | What it fixes | What was run |
|---|---|---|
| `pwsh-for-bash-writers` | The agent types `grep`, `head`, `tail`, `sed`, `awk`, `date -u`, `VAR=1 cmd`, heredocs, `2>/dev/null`, `for ... do ... done` or `&&` into PowerShell 7 and the call fails. | 49 bash-to-pwsh pairs, each run in PowerShell 7.6.3: the bash form fails or lies, the pwsh form prints the answer. Plus the quoting rules, exit codes, and a measured way to start a server without hanging the tool call. |
| `real-browser-automation` | The agent needs a real browser (real clicks and keys, `navigator.webdriver`, a beacon the browser sends itself) and reaches for a headless fake or a heavy package. | `scripts/cdp.mjs`, a 30 KB Node script with no packages that drives your installed Edge or Chrome over the DevTools protocol, loopback addresses only, three guard layers. Run against Edge 154 and Chrome 154; the measured values are in `references/measured.md`. |
| `bevy-rust-ecs` | The agent writes Bevy code from old tutorials and gets names that no longer exist (`SceneRoot`, `Camera3dBundle`, `EventReader`). | Every Bevy 0.19.1 name has its file and line in `references/verified-api.md`; a smallest working scene, a viewer recipe, and two Node scripts that check plugin versions and keep the sim outside Bevy. Read from the 0.19.1 source: nothing in it was compiled. |

## Requirements

- `pwsh-for-bash-writers`: a shell that is PowerShell 7. Measured on Windows 10 with PowerShell 7.6.3.
- `real-browser-automation`: Node 24 or newer, and Microsoft Edge or Google Chrome installed. Measured on Windows 10.
  Not tested on Linux or macOS.
- `bevy-rust-ecs`: Bevy 0.19.1 projects; the two scripts need Node 24.

## Install

1. Unzip `fleet-vol-1.zip`.
2. Copy the folders in `skills/` to `$HOME\.claude\skills` for Claude Code, or to `$HOME\.config\opencode\skills` for
   OpenCode (or the `.claude\skills` or `.opencode\skills` folder of one project).
3. A tool that takes one skill per zip uses `zips/<skill name>.zip`; SKILL.md is at the root of each.
4. Check: ask the agent which skills it has, or run `opencode debug skill --pure` in an OpenCode project.

The exact PowerShell commands are in `README.md` inside the zip. They were run against this zip by the test suite.

Try it in 15 minutes: in a PowerShell 7 agent session ask "show me the first two lines of notes.txt and count its
lines". With the skill loaded the agent uses `Get-Content -TotalCount 2` and `@(Get-Content ...).Count` instead of
`head` and `wc`. A stranger run of this check has not been done yet.

## Free sample (Vol 0)

`fleet-vol-1-vol0.zip` is `git-one-branch`, a skill for git in a repo that other sessions edit at the same time. It is
free, never sold, and licensed CC-BY-NC-SA-3.0 because it is derived from Pro Git (Scott Chacon and Ben Straub). It is
not in the paid zip. It shows the style of the pack: exact commands, the exact error text, tested against real git.
See `vol0-sample.md`.

## Price

$19 once. The pack is three skills, with every file listed in `manifest.json`. Take-home math is recomputed from the
store's own fee page on the day of listing, because fees change.

## Price evidence

Sellers' own pages for Claude Code skill packs, read 2026-10-04. They show what buyers are asked to pay today:

- https://a66273423.itch.io/claude-code-skills-master-pack: itch.io page, category Tool, minimum price $29 USD, 7 skills
  (Bash and SKILL.md files), one 12 kB zip.
- https://www.agentskillpacks.com/: 19 packs from $9 to $119, one-time payment, up to 37 skills in a pack, lifetime
  updates within version 1.
- https://pluginsdepo.com/store: a 7-skill bundle at $149 and a 15-skill stack at $99, with a 7-day money-back promise.

$19 sits under the $29 minimum of the 7-skill itch.io pack and above the $9 start of the cheapest packs; this pack has
fewer skills and every claim in it was run. The skills are in a public repository too (see Repository): you pay for
one tested, versioned download with its proof files, not for secrecy.

## Licences

- `pwsh-for-bash-writers`: CC-BY-4.0 and MIT. Rewritten from MicrosoftDocs/PowerShell-Docs (CC-BY-4.0 text, MIT code samples), commit a3de8f2.
- `real-browser-automation`: MIT, Apache-2.0 and BSD-3-Clause. The script and text are original (MIT); ideas from the Playwright docs (Apache-2.0); protocol names checked against the DevTools protocol files (BSD-3-Clause).
- `bevy-rust-ecs`: MIT and Apache-2.0. The text and scripts are original (MIT); facts read from the Bevy source, tag v0.19.1 (MIT OR Apache-2.0).
- No NonCommercial source is in the paid zip. `git-one-branch` (CC-BY-NC-SA-3.0) is the free Vol 0 only.
   Source licences re-read live 2026-10-05 via gh api (PowerShell-Docs repo spdx
   NOASSERTION with CC-BY-4.0 text and MIT code license files, Playwright
   Apache-2.0, devtools-protocol BSD-3-Clause, Bevy Apache-2.0, Pro Git repo
   spdx NOASSERTION with CC BY-NC-SA 3.0 license file; Pro Git stays
   NonCommercial and free): no source moved to NonCommercial, the pack stands.

The full credit lines are in `LICENSES.md` inside the zip.

## Proof

Each skill has a live proof: its tests ran against real programs and the skill still matches the fingerprint stored then.

- `pwsh-for-bash-writers`: 2026-10-05, 7 passed (one of them runs all 49 pairs in pwsh 7.6.3).
- `real-browser-automation`: 2026-10-05, 11 passed (real Edge and Chrome against 127.0.0.1).
- `bevy-rust-ecs`: 2026-10-05, 42 passed (names and file lines checked against the 0.19.1 source tree; nothing compiled).

The records are in `proof/` inside the zip.

## Store assets

Cover, demo and screenshots are delivered (paths below); none is faked. The page went live on 2026-10-04 before they existed (its cover list is empty), so `tools/pack_check.py` fails each missing one until the file is here.

- cover: store-art/O-025/out.png, store-art/O-025/out-630x500.png
  Delivered 2026-10-04 as order O-025: 1280x720 Gumroad cover and 630x500 itch card, plain design, no generated art.
- demo: store-art/O-033/demo.gif, store-art/O-033/out.png, store-art/O-033/out-630x500.png
  Delivered 2026-10-04 as order O-033: a real PowerShell session where `grep -n` fails with "is not recognized", then the same task with the skill loaded using `Select-String`. GIF is 480x288 15 s 167382 B (the brief asked 10 s 1280x720; the render gate makes 480x288, so it is listed as 15 s 480x288, not 1280x720); poster `out.png` 1280x720 and card `out-630x500.png` alongside.
- screenshots: store-art/shots/shot-pairs.png, store-art/shots/shot-wd.png, store-art/shots/shot-bevy.png
  Delivered 2026-10-04: three real 1280x800 PNG captures in a real Edge 154 over CDP: the pairs table of `references/pairs.md` (14 of 49 pairs, 64153 B), the JSON that `cdp.mjs --eval` prints for `navigator.webdriver` (`true`, HeadlessChrome/Edg 154, 27523 B), the old-name table of the Bevy skill (22 rows, 0 hits, 61620 B).

## Files

- `fleet-vol-1.zip`: the paid pack (README.md, LICENSES.md, manifest.json, skills/, zips/, proof/).
- `fleet-vol-1-vol0.zip`: the free Vol 0 skill (SKILL.md at the root, NOTICE.md).

## Changelog

- 2026-10-04: version 1.0.0 assembled. Contents tested, listing written, store assets requested.
- 2026-10-04: live on Gumroad at the Live listing line above; price $19 and the AI disclosure line stay as written.
