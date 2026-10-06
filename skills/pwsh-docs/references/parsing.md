# Parsing, escapes, and quoting

Facts checked against about_Parsing.md, about_Special_Characters.md, and about_Quoting_Rules.md at commit a3de8f22 (read 2026-10-06).

## Stop-parsing (--%)

Place `--%` between the program name and its arguments: `icacls X:\VMS --% /grant Dom\HVAdmin:(CI)(OI)F`. After the token the remaining line is literal. The only expansion left is `%NAME%` environment variables; an undefined name passes through as-is. The effect ends at the next newline or pipeline `|` character. Line continuation with a backtick does not extend it, and `;` does not terminate it. Stream redirection after `--%` is passed verbatim as an argument, not honored. Never needed for cmdlets; useful only for native Windows commands. The sibling token `--` (end-of-parameters) is for PowerShell commands: `Write-Output -- -InputObject` prints `-InputObject`.

## Escape sequences

Escape character is the backtick (ASCII 96), case-sensitive, honored only inside double-quoted strings. The task set: `` `n `` newline, `` `r `` carriage return, `` `t `` horizontal tab, `` `0 `` null, `` `a `` alert beep, `` `b `` backspace, `` `e `` escape, `` `f `` form feed, `` `v `` vertical tab, `` `u{x} `` unicode. There is no backslash-n in PowerShell: `"\n"` is backslash plus n, not a newline. The caret `^` never continues a line (that is cmd.exe).

## Line continuation

A backtick as the very last character of a line continues input on the next line. Any trailing space after it breaks the continuation and the error is hard to see. Prefer natural break points instead: after `|`, after binary operators (`+`, `-eq`), after `,`, after opening `[`, `{`, `(`. For long parameter sets prefer splatting (see startup-splatting.md).

## Quoting

Double-quoted strings expand: `$i` becomes its value, `$(2+3)` becomes `5`. Only basic `$name` references embed directly; anything with member access or indexing needs the subexpression form: `"PS version: $($PSVersionTable.PSVersion)"`. Separate a name from following text with braces: `"${HOME}: path"`. Escape a literal dollar with a backtick: `` `$ ``. Single-quoted strings are verbatim: `'$HOME'` stays as typed and `'$(2+3)'` never evaluates. There is no bash `${var}` expansion style; `${HOME}` in PowerShell is the brace disambiguation of `$HOME`.
