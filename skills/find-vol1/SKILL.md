---
name: find-vol1
description: Use when a task might fit a Fleet Vol 1 skill and you must answer which one fits plus its install command. Routes shell, browser, Bevy and shared-repo git tasks to the right Vol 1 skill, or says none fits.
version: 0.1.0
license: MIT
---

# Find the Vol 1 skill that fits

This skill answers one question: which Vol 1 skill fits the task, and how is it installed.
Every answer names exactly one skill (or none) and gives its install command.

## Answer shape

Answer in these three lines, in this order:

Skill: <skill name, or "none">
Why: <one plain sentence: the task signal that matches>
Install: <the command or path below for that skill>

Name only the four skills below. Never invent a name. When nothing fits, write
`Skill: none` and stop. Do not force a fit.

## The four skills

| Skill | It fits when the task hits ... | Install |
|---|---|---|
| pwsh-for-bash-writers | the Windows shell: grep, head, tail, wc, sed, awk, find, date -u, VAR=value, heredocs, 2>/dev/null, for/do/done, &&, quoting or exit codes | paid zip, folder `skills/pwsh-for-bash-writers`, or `zips/pwsh-for-bash-writers.zip` |
| real-browser-automation | a real browser: real clicks and keys, navigator.webdriver, a page beacon, CDP eval, driving Edge or Chrome on loopback | paid zip, folder `skills/real-browser-automation`, or `zips/real-browser-automation.zip` |
| bevy-rust-ecs | Bevy: an unknown Bevy name, an old-tutorial mismatch, a plugin version check, keeping the sim outside Bevy | paid zip, folder `skills/bevy-rust-ecs`, or `zips/bevy-rust-ecs.zip` |
| git-one-branch | git in a repo others edit: one shared branch, pull first, commit own paths, push, no rebase or force-push | free Vol 0 zip only, never sold |

The first three cost $19 as one zip, `fleet-vol-1.zip`. The fourth is the free
Vol 0 sample in `fleet-vol-1-vol0.zip` (CC-BY-NC-SA-3.0, derived from Pro Git),
free and never sold.

## Install commands

Paid skills (from the unpacked `fleet-vol-1.zip`):

```powershell
Expand-Archive -LiteralPath fleet-vol-1.zip -DestinationPath fleet-vol-1
$dest = "$HOME\.config\opencode\skills"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item -Recurse -Force -Path "fleet-vol-1\skills\*" -Destination $dest
```

Claude Code uses `$HOME\.claude\skills` instead, or one project's `.claude\skills`
or `.opencode\skills` folder. A tool that takes one skill per zip uses
`zips/<skill name>.zip`; SKILL.md sits at the root of each zip. Keep one copy
of a skill name per tool.

Free sample (from `fleet-vol-1-vol0.zip`): SKILL.md sits at the root; copy the
unpacked folder to the same skills path. It is free, never sold.

Check it loaded: ask the agent which skills it has, or run
`opencode debug skill --pure` in an OpenCode project.

## Say none

When the task fits no Vol 1 skill (a book-to-skill build, a store listing, a
skill audit, a demo GIF), answer:

Skill: none
Why: no Vol 1 skill covers <the task in five words or less>.
Install: none - do the task without Vol 1.
