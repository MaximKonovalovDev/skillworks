# Startup, splatting, pipelines, and chains

Facts checked against about_Pwsh.md, about_Splatting.md, about_Pipelines.md, and about_Pipeline_Chain_Operators.md at commit a3de8f22 (read 2026-10-06).

## pwsh startup

Inline snippet: `pwsh -NoProfile -Command "..."`. Whole file: `pwsh -NoProfile -File ./job.ps1`. `-NoProfile` skips all profiles. `-Command` must be the last flag because everything after it joins the command; `-File` must be last because everything after it joins the script path plus script args. A `-Command` string returning objects to another PowerShell host arrives deserialized, not live. Process exit code is 0 when `$?` is True and 1 when False, except natives and explicit `exit N` which collapse to 1 unless preserved: append `exit $LASTEXITCODE` to keep the exact code. Scheduled jobs use `-NonInteractive` plus `-NoProfile` and read `$LASTEXITCODE`, never `$?` alone.

## Splatting

Named parameters travel as a hashtable: `$HashArguments = @{Path = "test.txt"; Destination = "test2.txt"; WhatIf = $true}` then `Copy-Item @HashArguments`. The `@` sigil replaces `$` at the call site; `$` would pass one value, `@` spreads the collection into parameters. Hashtable keys map to parameter names by name, so order never matters; switches take `$true`/`$false`. Positional values travel as an array: `$array = '/c', 'dir'` then `cmd.exe @array`, order is position order. Since PowerShell 7.1 an explicit parameter overrides the splatted one.

## Pipelines

`|` connects commands into one left-to-right operation carrying objects, not text: `Get-Process notepad | Stop-Process` passes process objects, and `Get-ChildItem -Path *.txt | Where-Object {$_.Length -gt 10000} | Sort-Object -Property Length` passes FileInfo objects. Inside a block the current object is `$_` (alias `$PSItem`). There is no stdin on the PowerShell pipeline; native byte streams keep byte fidelity only for stdout-to-file and stdout-to-stdin paths.

## Pipeline chains

`&&` runs the right pipeline only when the left succeeded; `||` runs it only when the left failed. Both read `$?` (and `$LASTEXITCODE` for natives). `Write-Output 'First' && Write-Output 'Second'` prints both lines; `Write-Error 'Bad' && Write-Output 'Second'` prints only the error; `Write-Output 'First' || Write-Output 'Second'` prints only the first; `Write-Error 'Bad' || Write-Output 'Second'` prints the error then the second. Equivalence: `A && B` is `A; if ($?) { B }` and `A || B` is `A; if (-not $?) { B }`. Chains group left to right, bind looser than `|` and `>` but tighter than `;` and `=`, and never absorb a terminating error.
