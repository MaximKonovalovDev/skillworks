# Redirection and automatic variables

Facts checked against about_Redirection.md and about_Automatic_Variables.md at commit a3de8f22 (read 2026-10-06).

## Streams

Numbered streams: 1 Success (`Write-Output`), 2 Error (`Write-Error`), 3 Warning (`Write-Warning`), 4 Verbose (`Write-Verbose`), 5 Debug (`Write-Debug`), 6 Information (`Write-Information`, `Write-Host`). `*` means all streams. There is no stream 0 and no stdin on the pipeline; Success plus Error resemble stdout plus stderr but stdin is not connected. The Progress stream exists but cannot be redirected.

## Operators

`>` writes stream 1 to a file (overwrite without warning), `>>` appends, `n>` writes stream n, `n>>` appends stream n, `n>&1` folds stream n into Success. Only folds into Success exist; no stream folds into another numbered stream. Merge Error into Success: `dir C:\, fakepath 2>&1 > .\dir.log`. Merge everything: `.\script.ps1 *> script.log`. Suppress stream 6: `... 6> $null`. Writing uses UTF8NoBOM; `Out-File` adds `-Encoding`, `-Force`, `-Width`, `-NoClobber`. Bash order does not apply: `2>&1 > file` and `3>&1 2>&1 > file` fold first, then the combined Success stream lands in the file.

## Automatic variables

`$?` holds True when the last command succeeded and False when it failed; parse errors never set it. `$LASTEXITCODE` holds the native exit code (cmdlets never set it). `$_` and `$PSItem` hold the current pipeline object. `$Matches` holds the last `-match` groups. `$null`, `$true`, `$false` are constants. `$HOME`, `$PWD`, `$PROFILE`, `$PSHOME`, `$PSScriptRoot`, `$PSVersionTable` locate the session. `$args`, `$PSBoundParameters`, `$foreach`, `$switch`, `$this`, `$Error`, `$PID` serve their own contexts. Conceptually read-only: writing works for compatibility but scripts must not assign them.
