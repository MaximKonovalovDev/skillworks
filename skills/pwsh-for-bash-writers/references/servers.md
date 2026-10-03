# Starting a long-lived program without hanging the tool call

## What was measured
`scripts/hang_demo.mjs` plays the tool. It runs pwsh with piped output, starts a program that lives 12 s and then ends by itself, and times the call.
Run on Windows 10, pwsh 7.6.3, Node 24.14, 2026-10-03. Nothing was killed.

| How the program was started | call exited | output pipe closed |
|---|---|---|
| `node ... \| Select-Object -Last 1` (node starts the program) | 1.5 s | 13.5 s: waited for the program |
| `Start-Process -NoNewWindow` | 1.4 s | 13.4 s: waited for the program |
| `Start-Process -RedirectStandardOutput f -RedirectStandardError e` | 1.3 s | 13.5 s: waited for the program |
| `Start-Process cmd.exe /c "program > log 2>&1" -WindowStyle Hidden` | 1.6 s | 1.6 s: no wait, log filled |

The tool gets the end of the output only when every copy of the pipe is closed. A program started with an inherited handle holds a copy.
`Start-Process -RedirectStandardOutput` looks like the fix but it still passes the shell's own pipe to the new program. Windows copies every inheritable handle.
The last row worked in every run. The likely reason, not proven here: `Start-Process` without a redirect uses the Windows file launcher, which copies no handles, and cmd.exe does the redirect into the log.

This was measured with a Node harness that waits for the pipe to close. OpenCode's own shell tool was not run for this note.

## Recipe
Start, with the log inside the repo or the temp folder:
```
Start-Process -FilePath cmd.exe -ArgumentList '/c','node server.mjs > "logs/server.log" 2>&1' -WindowStyle Hidden
```
Wait until it is ready by reading the log or asking the program. Both calls end fast:
```
Start-Sleep 3; Get-Content logs/server.log -Tail 20
Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 http://127.0.0.1:8080/health | Select-Object -ExpandProperty StatusCode
```
Use the full path of the log if the working folder may change.

## Rules
- A script that ends by starting a server must start it this way, never with `&`, `Start-Process -NoNewWindow` or a redirect switch.
- Never wrap such a script in `| Select-Object -Last N`. Write its output to a file and read the file.
- Stop the server with its own stop command or stop script. Do not kill processes.
- If a call has already hung, end the step and report BLOCKED with the command text.
