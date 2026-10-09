---
name: pwsh-docs
description: Use when writing PowerShell parsing, quoting, comparison, splatting, redirection, pipeline-chain, or pwsh startup code that bash-trained authors get wrong: stop-parsing, escape sequences, quote expansion, case-insensitive operators, splat sigils, stream numbers, and chain operators with the exact syntax to type. For translating bash commands to pwsh use pwsh-for-bash-writers instead.
version: 0.1.0
author: skillworks
license: MIT
---

# PowerShell docs distilled

Fix-first rules distilled from MicrosoftDocs PowerShell-Docs (a3de8f22) for the pwsh confusion class: how native arguments survive parsing, which quotes expand, which operator compares, how a long call stays readable, where each stream goes, and which variable the chain consults. Each rule names the exact token to type and the output fragment that proves it. Longer notes live in references/: per-group facts, glossary.md, patterns.md, and cheatsheet.md.

## Parsing and quoting

- Put the stop-parsing token `--%` before native-program arguments as `prog --% args`; the `remaining` line stays literal except `%VAR%` environment references, it reaches only to the next `newline` or pipeline `|` character, and it is for `native` commands only, never needed for cmdlets [src: about_Parsing.md]
- Write newline as `` `n ``, carriage return as `` `r ``, and horizontal tab as `` `t `` inside `"double"` strings only; continue a long line with a backtick `` ` `` as the last character of the line with no trailing space (line continuation) [src: about_Special_Characters.md]
- `"double"` strings expand `$x` and embedded `$(expr)` while `'single'` strings stay literal; embed member access or indexing only through the subexpression `$(...)` as in `"version $($PSVersionTable.PSVersion)"` [src: about_Quoting_Rules.md]

## Comparison and operators

- Compare with the `-eq` family (`-eq`, `-ne`, `-gt`, `-ge`, `-lt`, `-le`); matching is case-insensitive by default, the `c` prefix `-ceq` selects case-sensitive matching, the `i` prefix `-ieq` makes insensitivity explicit, and `'ABC' -ceq 'abc'` returns `False` [src: about_Comparison_Operators.md]
- Never use `==` or `===` for equality and never use `>` or `<` for numeric comparison: `>` writes a file, so test size with `-gt` and `-lt` and combine conditions with `-and`, `-or`, and `-not` [src: about_Operators.md]

## Startup, splatting, and flow

- Start inline code with `pwsh -NoProfile -Command "..."` and a script file with `pwsh -NoProfile -File ./job.ps1`; `-NoProfile` skips profiles, and the exact native exit code survives only through `exit $LASTEXITCODE` [src: about_Pwsh.md]
- Splat a long call with the `@` sigil over a `hashtable` as in `$splat = @{Path='b.txt'; Value='hi'}; Set-Content @splat`; each hashtable key maps to one `parameters` name, while `@arr` arrays only fill positional slots [src: about_Splatting.md]
- Send objects down the pipeline with `|` as in `Get-ChildItem -Path *.txt | Where-Object {$_.Length -gt 10000}`; commands run left to right as one operation and the current object inside the block reads as `$_` [src: about_Pipelines.md]
- Chain with `&&` (run right only when left succeeded) and `||` (run right only when left failed); both consult `$?`, so `Write-Output chain-ok && Write-Output chain-second` prints `chain-ok` then `chain-second` [src: about_Pipeline_Chain_Operators.md]

## Redirection and state

- Redirect with `>` (write), `>>` (append), `n>` (stream n), and `n>&1` (fold stream n into Success); stream `1` is Success (`Write-Output`) and stream `2` is Error (`Write-Error`), so `2>&1` merges Error into Success and `*>` merges every stream into one file [src: about_Redirection.md]
- Read status from `$?` (`True` when the last command succeeded, `False` when it failed), the native code from `$LASTEXITCODE`, and the current pipeline object from `$_` (alias `$PSItem`); chain operators test `$?`, scheduled jobs test `$LASTEXITCODE` [src: about_Automatic_Variables.md]

## Fix-first workflow

Run the failing line with pwsh -NoProfile -Command and read the symptom: mangled native flags need the stop-parsing rule, a literal $x needs the quoting rule, a wrong string test needs the comparison rule, an unreadable call needs the splatting rule, a lost error needs the redirection rule, a skipped second command needs the chain rule. The per-symptom recipes are in references/patterns.md and the one-page reminder in references/cheatsheet.md.
