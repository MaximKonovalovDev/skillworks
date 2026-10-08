# Patterns: symptom to branch

Each recipe starts from a sed-replace miss the loop really makes, then names the one branch that fixes it. All replays ran on this PC on 2026-10-08.

## Regex escaping pain

Symptom: the loop fights sed backslashes escaping special chars.

- Use `String-literal mode` with `-F` or `fixed-strings`; no `backslashes` escaping (pair `sd-p01`).
- prints: `lit PASS literal-no-regex`

## Sed one-liners feel fine

Symptom: a reviewer claims sed one-liners are fine.

- Write `sd before after` instead of `sed s/before/after/g`; newline needs `-A` `across mode` (pair `sd-p02`).
- prints: `sed PASS simpler-than-sed`

## Special chars must go

Symptom: ((([]))) must be stripped without regex.

- Pass `-F` `fixed-strings`; the `lots of special chars` example prints clean (pair `sd-p03`).
- prints: `lots PASS literal-example`

## Parts need numbers

Symptom: cmd plus channel plus subcmd must come from one match.

- Use `capture groups` with `$1` refs; `named capture` yields `dollars` and cents (pair `sd-p04`).
- prints: `grp PASS dollar-groups`

## Dollars print empty

Symptom: the replacement prints empty where dollars stood.

- Resolve `ambiguities` with `${var}` braces for `dollars_dollars` (pair `sd-p05`).
- prints: `brace PASS braced-dollars`

## Blind file edits

Symptom: the loop edits http.js without seeing the change.

- Bare sd edits `http.js` `in-place`; add `-p` to `preview` first (pair `sd-p06`).
- prints: `prev PASS preview-first`

## Newline never matches

Symptom: the \n pattern never matches across lines.

- Default is `line by line`; use `-A` `across` to join hello and world (pair `sd-p07`).
- prints: `acr PASS across-newline`

## Dashes and dollars vanish

Symptom: -w is eaten as a flag and $bar vanishes.

- Put `--` for `end of flags`; double `$$` to print `$bar` (pair `sd-p08`).
- prints: `esc PASS dash-dollar-escape`
