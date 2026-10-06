# Fix patterns per symptom

Each pattern: symptom, the rule, the sanctioned fix, and how to confirm. All outputs below were run with pwsh 7.6 on 2026-10-06.

## Native flags mangled

Symptom: a native call evaluates quotes and parens (`cmd /c echo "a|b"` errors with `is not recognized`). Fix: insert `--%` before the native arguments (`cmd /c --% echo "a|b"` prints `"a|b"`). Confirm: the remaining line arrives literal except `%VAR%`.

## Wrong line endings or columns

Symptom: a file needs CRLF plus tabs but the script writes backslash-n text. Fix: use `` `r`n `` for CRLF and `` `t `` for tabs inside a double-quoted string. Confirm: the bytes contain carriage return plus newline and tab stops.

## Literal $x where a value belongs

Symptom: output shows `single:$x` when `double:world` was intended. Fix: switch to double quotes, and wrap member access in a subexpression (`"version $($o.Count)"`). Confirm: rerun prints the value, not the name.

## String test goes the wrong way

Symptom: `==` or `===` used, or case assumed sensitive. Fix: use `-eq` for insensitive equality, `-ceq` for sensitive, `-ieq` to state insensitivity. Confirm: `'ABC' -ceq 'abc'` prints False while `'ABC' -eq 'abc'` prints True.

## Scheduled job loads profiles or loses its code

Symptom: a job behaves differently by machine or always reports 0/1. Fix: start with `pwsh -NoProfile -Command` (snippet) or `pwsh -NoProfile -File` (script) and end the command with `exit $LASTEXITCODE`. Confirm: profiles never load and the exact native code returns.

## Ten-parameter call is unreadable

Symptom: one cmdlet line carries ten named parameters. Fix: pack them into `$splat = @{...}` and call `Cmdlet @splat`. Confirm: `@` replaces `$` at the call and every key matches a parameter name.

## Errors vanish or flood the console

Symptom: errors print while success should go to a file, or nothing is captured. Fix: capture errors with `2>&1` and merge everything with `*>`. Confirm: `dir C:\, fakepath 2>&1 > .\dir.log` lands both streams in the file.

## Second command never runs (or always runs)

Symptom: `&&` or `||` behaves like plain `;`. Fix: check `$?` semantics: `&&` needs True, `||` needs False. Confirm: `Write-Output chain-ok && Write-Output chain-second` prints both lines.

## `>` compared instead of redirecting

Symptom: `if (36 > 42)` writes a file named `42` instead of testing. Fix: compare with `-gt`/`-lt` and redirect with `>`/`>>` only for files. Confirm: no file named `42` appears and the test returns False.
