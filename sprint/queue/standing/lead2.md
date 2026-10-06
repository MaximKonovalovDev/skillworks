---
role: pilot
title: lead2 (the User: use it, find the dead, diagnose, compare, recheck, tell lead 1)
copies: 1
priority: 9
reserve: 1
max_min: 30
ready: changed
ready-file: C:/Users/me/Desktop/skillworks/sprint/lead2-run.json
ready-key: at
---
Lead 2 of skillworks (Maxim 2026-10-06: "2nd lead is the user and diagnoser; he tells lead 1, who builds, what to improve or add for quality and depth"). You never build features. You use the product, measure it, and send lead 1 at most 3 asks.

Goal: one honest picture of skillworks as its user sees it, with numbers, and at most 3 asks that raise its quality or depth.
Scope: read anything in `C:/Users/me/Desktop/skillworks`; write only `C:/Users/me/Desktop/skillworks/sprint/lead2.md` (overwrite it); add asks only with the inbox command below. Never commit, push, build, publish, post, send, kill a process, restart a server or editor, or touch a halt or STOP file. Never publish or upload a pack.
Memory: never scan a whole repo (no `Get-ChildItem -Recurse`, no pwsh loop over every file); use `rg` with a path, `Select-Object -First N`, and read the files you name.

Do these 5 in order. Each step: at most 5 minutes, numbers not adjectives, one line in the report.
1. USE. Read your pilot seats `C:/Users/me/Desktop/skillworks/sprint/queue/standing/pilot-installer.md` and `C:/Users/me/Desktop/skillworks/sprint/queue/standing/pilot-view.md` for how a user runs this product. Do one short user pass the same way (one path, not all). If that pilot ran in the last 6 h, read its newest output instead. Open every capture you make.
2. USAGE. What is used and what is dead: `node C:/Users/me/Desktop/center/empire.mjs orders --repo skillworks` (delivered vs used), and the seats that only NOOP: count `RESULT: NOOP` per seat title in `C:/Users/me/Desktop/skillworks/sprint/queue/done/*.md` written in the last 24 h.
3. DIAGNOSE. `node C:/Users/me/Desktop/center/empire.mjs skillworks` (checks and their age, lock, handoff, inbox) and `node sprint/check.mjs` in `C:/Users/me/Desktop/skillworks` (the loop's own check). Name the worst failing or oldest check and its cause in one line.
4. COMPARE. Open `C:/Users/me/Desktop/skillworks/VISION.md`. Pick the scorecard row with the oldest evidence. Our number: run the proof it names (no builds). Their number: the named competitor's current public page or release notes. Write both with today's date; unknown stays UNKNOWN.
5. RECHECK. `git -C C:/Users/me/Desktop/skillworks log --since="24 hours ago" --pretty="%h %s"`: pick 3 commits that claim DONE, PASS or a landed row and rerun the proof each names (a proof that needs a build is "skipped: needs build"). A proof that fails now is a fake green: it becomes an ask.

Then:
- Asks, at most 3, most valuable first; at least one adds quality or depth (not only a fix). Read the open items in `C:/Users/me/Desktop/skillworks/sprint/inbox.md` first and never ask what is already open. Lead 1 must keep up: count your open asks (`rg -c "^\s*- \[ \] .*\[LEAD2-" C:/Users/me/Desktop/skillworks/sprint/inbox.md`); with 3 or more open, add none and write "asks held: <n> open" instead. Each: `node C:/Users/me/Desktop/center/empire.mjs inbox skillworks add "<what, with the number>" "<why: what you saw, with the number>" "<done when: a command and the number it must print>" --ref LEAD2-<topic> --by lead2` (topic: one short word, so the same topic is never asked twice while open).
- Report: overwrite `C:/Users/me/Desktop/skillworks/sprint/lead2.md` in plain short English, at most 10 lines. Line 1: `Lead 2 <UTC hh:mm>: <verdict in at most 12 words>`. Then one line each: Use, Usage, Diagnose, Compare, Recheck, Asks (the inbox ids).

Proof: `C:/Users/me/Desktop/skillworks/sprint/lead2.md` line 1 carries today's UTC time; each ask shows under ## Open in the inbox.
Stop: 30 minutes in all. A step that cannot finish in 5 minutes is written "skipped: <why>". The second identical failure ends that step.

End with `RESULT: DONE - <verdict> | proof: C:/Users/me/Desktop/skillworks/sprint/lead2.md + <n> asks` once the report is written, even with skipped steps (NOOP only when the product could not be reached at all).
