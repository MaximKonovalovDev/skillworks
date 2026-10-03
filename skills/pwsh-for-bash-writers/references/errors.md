# Error text -> cause -> fix

Each fragment below is real output from a failed pair in `pairs.md`. The test reruns the pair and checks the fragment is in the error.

- `is not recognized`: you typed a Unix word (grep, head, tail, wc, sed, awk, touch, which, seq, xargs, basename, python3, time, export) or a `NAME=value` prefix. Pair `grep-line`. Use the pwsh form from SKILL.md.
- `The term '=' is not recognized`: a command in double quotes held `$x = 5`. The outer pwsh filled in `$x` first. Pair `nested-pwsh`. Use single quotes around the inner command.
- `Missing opening '('`: a bash `for f in a b; do ... done` loop. Pair `for-loop`. Write `foreach ($f in 'a','b') { ... }`.
- `Unexpected token '&&'`: `&&` after foreach, if or while. Pair `and-after-statement`. Write `; if ($?) { ... }`.
- `Missing type name`: a bash test `[ -f x ]`. Pair `test-file`. Write `Test-Path -LiteralPath x -PathType Leaf`.
- `Missing file specification after redirection operator`: a heredoc `<<EOF`. Pair `heredoc`. Use a here-string or the Write tool.
- `Variable reference is not valid`: `"$name: text"`. Pair `colon-in-string`. Write `"${name}: text"`.
- `No characters are allowed after a here-string header`: text after `@'` on the same line. Pair `here-string-header`. Put a newline right after `@'`.
- `A parameter cannot be found that matches parameter name`: a bash flag on a pwsh alias, for example `ls -la` or `rm -rf`. Pair `ls-flags`. Use `Get-ChildItem -Force`, `Remove-Item -Recurse -Force`.
- `is ambiguous`: `date -u` or `echo -e`. Pair `date-utc`. Use `Get-Date -AsUTC -Format '...'` and `"a`nb"`.
- `Could not find a part of the path`: you wrote `2>/dev/null`. Pair `dev-null`. Write `2>$null` or `*> $null`.
- `does not exist, or has been filtered`: a file name with `[ ]` given to `-Path`. Pair `wildcard-path`. Use `-LiteralPath`.
- `Cannot find path`: a Git Bash path like `/c/Windows/x`. Pair `git-bash-path`. Write `C:/Windows/x`.
- `os error 123`: a `*` given to a program such as rg. Pair `native-glob`. Use `-g '*.md'` or a cmdlet.
- `File not found`: `find` is the Windows find.exe. Pair `find-name`. Use `Get-ChildItem -Recurse -Filter`.
- `SyntaxError`: JavaScript with `\"` inside double quotes. Pair `node-e-quotes`. Put the script in single quotes or in a file.
