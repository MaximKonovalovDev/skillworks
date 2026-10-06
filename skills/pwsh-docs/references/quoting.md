# Quoting proofs and string traps

Facts checked against about_Quoting_Rules.md at commit a3de8f22 (read 2026-10-06). Every line below was run with pwsh 7 on 2026-10-06.

## The two rules

Double expands, single does not. `$x='world'` then `"double:$x"` prints `double:world` while `'single:$x'` prints `single:$x`. That pair is trial pd-r01 and the fastest proof that the rule holds in the live shell.

## Traps for bash authors

A backslash never escapes a quote: `"say \"hi\""` ends early, write `'say "hi"'` instead. A colon after a name is a scope marker: `"$HOME: x"` fails, write `"${HOME}: x"`. A member access without a subexpression prints the object: `"$o.Count"` is wrong, write `"$($o.Count)"`. Code meant for another program (`node -e`, `pwsh -Command`) goes in single quotes so the outer shell does not expand its `$` first.

## Here-strings

A here-string opener `@'` or `@"` must end its line and the closer `'@` or `"@` must start its line. Single-quoted here-strings stay verbatim, double-quoted ones expand like double-quoted strings.
