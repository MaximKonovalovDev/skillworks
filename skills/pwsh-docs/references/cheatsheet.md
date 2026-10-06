# pwsh-docs cheatsheet

One line per rule. Every line below matches a trial task in evals/pwsh-docs_trials.jsonl.

Parsing: `prog --% args` keeps the remaining line literal to newline or `|`; native only, never cmdlets. (pd-a01)

Escapes: `` `n `` newline, `` `r `` carriage return, `` `t `` tab in double strings; trailing backtick continues the line. (pd-a02)

Quoting: `"double:$x"` expands to `double:world`; `'single:$x'` stays literal; member access needs `"... $($o.P) ..."`. (pd-a03, pd-r01)

Comparison: `-eq` family, insensitive default; `-ceq` sensitive; `-ieq` explicit; `'ABC' -ceq 'abc'` is False. (pd-a04, pd-r02)

Startup: `-Command` inline text, `-File` script file, `-NoProfile` skip profiles, `exit $LASTEXITCODE` keep the code. (pd-a05)

Splatting: `@Hash` over `@{Path=; Value=}` maps keys to parameter names; `@arr` is positional only. (pd-a06, pd-r03)

Redirection: `>` write, `>>` append, `2>&1` Error into Success, `*>` all streams; `1` Success, `2` Error. (pd-a07, pd-r04)

Chains: `&&` when `$?` True, `||` when `$?` False; `Write-Output chain-ok && Write-Output chain-second` prints both. (pd-r05)

Pipelines: `A | B` passes objects left to right; `$_` is the current object.

Operators: compare with `-gt -lt`, join with `-and -or -not`; `>` writes files, `<` is reserved.

State: `$?` last status, `$LASTEXITCODE` native code, `$_` current object.
