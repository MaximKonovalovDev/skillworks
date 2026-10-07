# Error lines the pairs replay (all thrown live by scripts/run_bat.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the fixed-query report instead.

- `cat(1) clone`: called bat an editor that rewrites files. Pair `bt-p01`
- `pipes its own output to a pager`: let output scroll with no pager. Pair `bt-p02`
- `non-interactive terminal`: expected styled output in a pipe. Pair `bt-p03`
- `bat -n`: showed grid plus header instead of numbers only. Pair `bt-p04`
- `BAT_PAGER`: set PAGER and lost the precedence. Pair `bt-p05`
- `PagerSource`: guessed the pager origin. Pair `bt-p06`
- `PagerKind`: listed two pagers and missed the rest. Pair `bt-p07`
- `from_bin`: mapped pager names by hand. Pair `bt-p08`
- `missed syntax highlighting`: queried plain.txt for the highlight phrase. Pair `bt-p09`
- `missed line numbers`: queried plain.txt for the numbers phrase. Pair `bt-p10`
- `missed Pager`: queried plain.txt for the pager enum. Pair `bt-p11`
- `missed BAT_PAGER`: queried plain.txt for the pager variable. Pair `bt-p12`
