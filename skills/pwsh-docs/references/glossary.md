# pwsh-docs glossary

Short meanings as the PowerShell docs use them. Quoted lines are the exact token the skill checks.

- stop-parsing: the `--%` token ending PowerShell interpretation for the remaining line; native commands only.
- end-of-parameters: the `--` token ending parameter binding for PowerShell commands.
- escape: the backtick character quoting the next character; `` `n `` newline, `` `r `` carriage return, `` `t `` tab.
- line continuation: a backtick as the last character of a line joining it to the next; any trailing space breaks it.
- expandable string: a `"double"` string filling `$name` and `$(expr)` before the command runs.
- verbatim string: a `'single'` string passed exactly as typed with no substitution.
- subexpression: `$(...)` embedding any expression inside an expandable string.
- equality family: `-eq -ne -gt -ge -lt -le` plus `i`/`c` case variants; `-ceq` sensitive, `-ieq` explicit insensitive.
- splatting: passing a collection with `@` instead of `$`; `@{...}` hash tables by name, `@(...)` arrays by position.
- hashtable: `@{Name = value; ...}` mapping parameter names to values for a splatted call.
- stream: numbered output channel; `1` Success, `2` Error, `3` Warning, `4` Verbose, `5` Debug, `6` Information, `*` all.
- redirection: `>` write, `>>` append, `n>` stream n, `n>&1` fold into Success, `*>` every stream to a file.
- pipeline: commands joined by `|` passing objects left to right; `$_` is the current object.
- chain: `&&` (right runs when left succeeded) and `||` (right runs when left failed), both consulting `$?`.
- startup flags: `-Command` inline text, `-File` script path, `-NoProfile` skip profiles, `exit $LASTEXITCODE` keep the code.
- automatic variables: `$?` last status, `$LASTEXITCODE` native code, `$_` current object, `$Matches` last regex groups.
