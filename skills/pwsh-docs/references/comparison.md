# Comparison and operators

Facts checked against about_Comparison_Operators.md and about_Operators.md at commit a3de8f22 (read 2026-10-06).

## Equality family

Equality is `-eq`, not `==`; there is no `===` in PowerShell. Full equality set: `-eq`, `-ne`, `-gt`, `-ge`, `-lt`, `-le` with `i`/`c` variants (`-ieq`, `-ceq`, `-igt`, `-cgt`, and so on). String comparison is case-insensitive by default: `'ABC' -eq 'abc'` is True. The `c` prefix selects case-sensitive: `'ABC' -ceq 'abc'` is False. The `i` prefix states insensitivity explicitly: `'ABC' -ieq 'abc'` is True. Types convert toward the left side: `2 -eq '2'` is True. Against a collection the operator filters: `1,2,3 -eq 2` returns `2`, and with no match it returns an empty array.

## Matching, containment, type

Matching: `-like` (wildcard `*` `?`), `-match` (regex, fills `$Matches`), `-replace` (regex replace), each with `-not` and `i`/`c` variants. Containment: `-contains`, `-notcontains`, `-in`, `-notin`. Type: `-is`, `-isnot`. Containment and type operators always return a Boolean.

## Arithmetic, logical, redirection trap

Arithmetic: `+ - * / %` (plus `+= -= *= /= %=` assignment, `-band -bor -bxor -bnot -shl -shr` bitwise). Logical: `-and -or -xor -not !`. The `>` character never compares: `if (36 > 42)` writes `36` into a file named `42`. Numeric comparison always uses `-gt` and `-lt`. The `<` character is reserved and parses as an error.
