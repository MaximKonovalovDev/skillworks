---
name: pwsh-for-bash-writers
description: Use before writing ANY shell command on this Windows PC. The shell is PowerShell 7 (pwsh), not bash, so grep, head, tail, wc, sed, awk, find, date -u, time, VAR=value, $(...), heredocs, 2>/dev/null, for/do/done and && after a statement fail. Gives the tested pwsh form of each, the quoting rules, exit codes, and how to start a server without hanging the tool call.
license: CC-BY-4.0 (PowerShell-Docs text), MIT (PowerShell-Docs code samples, this skill's scripts)
---

# Shell on this PC is pwsh, not bash

The shell tool runs `pwsh -NoLogo -NoProfile -NonInteractive -Command "<your text>"`.
That is PowerShell 7. Git's grep, head, tail, wc and sed are often not on PATH.
Agents lose many tool calls to "is not recognized" and to parser errors. This skill removes both.

## Rule 0: keep file work out of the shell
Use Read (offset, limit) instead of head, tail, sed -n. Use Grep instead of grep. Use Glob instead of find and ls.
Use Edit instead of sed -i. Use Write instead of heredocs and echo >. The shell is for running programs: node, python, cargo, git, rg.

## Bash habit -> pwsh (every line was run; the full list is `references/pairs.md`)
- `grep -n TODO notes.txt` -> `Select-String -Path notes.txt -Pattern TODO`
- `grep -c TODO notes.txt` -> `(Select-String -Path notes.txt -Pattern TODO).Count`
- `Get-Content notes.txt | grep TODO | head -n 1` -> `Get-Content notes.txt | Select-String TODO | Select-Object -First 1`
- `head -n 2 notes.txt` -> `Get-Content notes.txt -TotalCount 2`
- `tail -n 2 notes.txt` -> `Get-Content notes.txt -Tail 2`
- `wc -l notes.txt` -> `@(Get-Content notes.txt).Count`
- `sed -n '2,3p' notes.txt` -> `Get-Content notes.txt | Select-Object -Skip 1 -First 2`
- `sed 's/TODO/DONE/' notes.txt` -> `(Get-Content notes.txt) -replace 'TODO','DONE'`
- `awk '{print $2}' notes.txt` -> `Get-Content notes.txt | ForEach-Object { ($_ -split '\s+')[1] }`
- `find . -name '*.md'` -> `Get-ChildItem -Recurse -Filter *.md | ForEach-Object Name`
- `ls -la` -> `Get-ChildItem -Force | ForEach-Object Name`
- `which node` -> `(Get-Command node).Source`
- `touch x.txt` -> `if (-not (Test-Path x.txt)) { New-Item -ItemType File x.txt | Out-Null }; Test-Path x.txt`
- `date -u +%Y-%m-%dT%H:%MZ` -> `Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mmZ'`
- `UTC=$(date -u +%FT%TZ); echo $UTC` -> `$utc = Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mmZ'; $utc`
- `time node --version` -> `$sw = [Diagnostics.Stopwatch]::StartNew(); node --version; 'seconds: ' + [math]::Round($sw.Elapsed.TotalSeconds, 1)`
- `FOO=1 node -e 'console.log(process.env.FOO)'` -> `$env:FOO = '1'; node -e 'console.log(process.env.FOO)'`
- `node -e 'process.exit(3)' >/dev/null 2>&1; echo $LASTEXITCODE` -> `node -e 'process.exit(3)' *> $null; $LASTEXITCODE`
- `for f in a b; do echo $f; done` -> `foreach ($f in 'a','b') { $f }`
- `[ -f notes.txt ] && echo yes` -> `Test-Path -LiteralPath notes.txt -PathType Leaf`
- `python3 --version` -> `python --version`
- `diff notes.txt other.txt` -> `Compare-Object (Get-Content notes.txt) (Get-Content other.txt)`
- `powershell -NoProfile -Command "Get-Date -AsUTC"` -> `pwsh -NoProfile -Command "Get-Date -AsUTC"`

Also true: `rg -n TODO notes.txt` works (ripgrep is installed). `cmd1 && cmd2` works between two commands.
After foreach or if it is an error: write `foreach ($f in 'a','b') { $f }; if ($?) { 'after' }`.
Plain `diff` compares the two file NAMES and prints nothing useful. `find` is the old Windows find.exe.

## Quotes: the cause of most parser errors
- Single quotes keep every character. Double quotes fill in `$x`, `$(expr)` and the backtick. Default to single quotes. A quote inside single quotes is doubled: `'it''s'`.
- A backslash does not escape a quote. `"say \"hi\""` ends early. Use `'say "hi"'`.
- `"$name: x"` will not parse. Write `"${name}: x"`. `"$o.a"` prints the object. Write `"$($o.a)"`. `"price $450"` loses `$450`. Write `'price $450'`.
- Code for another program (`node -e`, `pwsh -Command`, `python -c`) goes in single quotes: `node -e 'console.log("hi")'`.
  Inside double quotes the outer pwsh fills in every `$` first. For more than one line, write a file with the Write tool and run it.
- A here-string opener `@'` must end its line, and the closer `'@` must start its line.

## Paths and programs
- Use `-LiteralPath` for any name you did not make. With `-Path`, `[` `]` `*` `?` are wildcards.
- Write `C:/Users/x` or `C:\Users\x`. Never `/c/Users/x`.
- Programs do not get `*` expanded. Write `rg -n TODO sub -g '*.md'`, not `rg -n TODO sub/*.md`. Cmdlets do expand: `Select-String -Path sub/*.md -Pattern TODO`.
- A program path with a space needs the call operator: `& '.\my tools\hello.cmd'`.
- Write `curl.exe`, not `curl`.

## Exit codes
- `$LASTEXITCODE` is the exit code of the last program. `$?` is only True or False.
- A failing program never stops the script, even with `$ErrorActionPreference = 'Stop'`. Test it: `node build.mjs; if ($LASTEXITCODE -ne 0) { 'build failed' }`.
- `node x.mjs 2>&1 | Select-Object -Last 20; $LASTEXITCODE` still gives the exit code of node.

## Never hang the tool call (measured, see `references/servers.md`)
A call is over when the shell has exited AND its output pipe has closed.
A server you start keeps a copy of that pipe, so the call waits until the server dies. Forever, for a gateway.
- Never pipe a command that starts a server into `Select-Object -Last N`.
- `Start-Process -NoNewWindow` and `Start-Process -RedirectStandardOutput` hang the call too. They were measured.
- Start it like this, then read the log:
  `Start-Process -FilePath cmd.exe -ArgumentList '/c','node server.mjs > "logs/server.log" 2>&1' -WindowStyle Hidden`
  `Get-Content logs/server.log -Tail 20`
- Stop it with the program's own stop command. Do not kill processes. If a call hangs, end the step and report BLOCKED.

## When a command fails
Fix the cause once. Do not send the same text again. The error text names the cause: look it up in `references/errors.md`.
