# Fleet Vol 1: three tested skills for coding agents

Version 1.0.0. Three Agent Skills (folders with a `SKILL.md`) for Claude Code, OpenCode and any other tool that reads
`SKILL.md` folders. Each one fixes a mistake coding agents repeat, and every claim in it was run on a real program before
it was written down.

| Skill | What it fixes |
|---|---|
| `pwsh-for-bash-writers` | The agent types bash (`grep`, `head`, `sed`, `date -u`, heredocs, `&&`) into PowerShell 7 and the call fails. Gives the tested pwsh form of 49 habits, the quoting rules and how to start a server without hanging the call. |
| `real-browser-automation` | The agent needs a real browser, not a headless fake. A zero-dependency Node script drives the Edge or Chrome you already have over the DevTools protocol, loopback only. |
| `bevy-rust-ecs` | The agent writes Bevy code from old tutorials and gets names that no longer exist. Every name is checked against Bevy 0.19.1 with file and line. |

## Requirements

- `pwsh-for-bash-writers`: a shell that is PowerShell 7. Written and measured on Windows 10 with PowerShell 7.6.3.
- `real-browser-automation`: Node 24 or newer and an installed Microsoft Edge or Google Chrome. Measured on Windows 10
  with Edge 154 and Chrome 154. Not tested on Linux or macOS.
- `bevy-rust-ecs`: nothing to run to read it; its two scripts need Node 24. It targets Bevy 0.19.1. Everything in it was
  read from the 0.19.1 source; none of it was compiled.

## Install

Unpack the zip, then copy the skill folders to where your agent looks for skills. In PowerShell 7:

```powershell
Expand-Archive -LiteralPath fleet-vol-1.zip -DestinationPath fleet-vol-1
$dest = "$HOME\.claude\skills"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item -Recurse -Force -Path "fleet-vol-1\skills\*" -Destination $dest
```

- Claude Code: `$HOME\.claude\skills` (every project) or `.claude\skills` inside one project.
- OpenCode: `$HOME\.config\opencode\skills` (every project) or `.opencode\skills` inside one project.
- A tool that takes one skill per zip: use `zips\<skill name>.zip` (SKILL.md is at the root of each).
- Keep one copy of a skill name per tool. Two folders with the same name make some tools list it twice.

Check that it loaded: ask the agent which skills it has, or in OpenCode run `opencode debug skill --pure` in the project.

## Licences

Each skill keeps the licence of its sources. `LICENSES.md` has the credit line for each. The text and scripts you bought
may be used and changed under those licences. Do not remove the credits.

## Proof

`proof/<skill>-live-proof.json` is the record of the last run of that skill's live tests: date, result line, and the
versions of Python, Node, PowerShell and git it ran with. `manifest.json` lists every file with its size and sha256.

## Limits

- Values measured on one Windows 10 PC can differ on yours. The skills say which version each number came from.
- No support is promised. The skills are text and scripts you can read and change.
