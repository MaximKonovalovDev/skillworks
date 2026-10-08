# Patterns: symptom to branch

Each recipe starts from a diff-read miss the loop really makes, then names the one branch that fixes it. All replays ran on this PC on 2026-10-07.

## Diff read as a rewrite fear

Symptom: the loop avoids delta, fearing it rewrites history.

- delta is a `syntax-highlighting pager` for `git` plus `diff` plus `grep` output (pair `dd-p01`).
- prints: `delta PASS pager-for-diffs`

## Diffs scroll with no pager

Symptom: plain git diff scrolls with no styling.

- Set `pager = delta` plus `diffFilter` to `delta --color-only` (pair `dd-p02`).
- prints: `wire PASS pager-filter-wired`

## Changed words invisible

Symptom: long changed lines hide which words changed.

- Highlight at `Word-level` with `Levenshtein` `edit inference` (pair `dd-p03`).
- prints: `word PASS word-level-edits`

## Unified diff unreadable wide

Symptom: unified diff is unreadable on a wide monitor.

- Set `side-by-side = true` with `line-numbers` on; long lines `wraps` (pair `dd-p04`).
- prints: `side PASS two-panel-wraps`

## Forty files paged by hand

Symptom: paging a 40-file diff scrolls by hand.

- Set `navigate` to true, press `n and N` between `diff sections` (pair `dd-p05`).
- prints: `nav PASS jump-between-diffs`

## Numbers lost in two panels

Symptom: side-by-side loses line numbers.

- The panel enables `line-numbers` with `left-format` columns (pair `dd-p06`).
- prints: `feat PASS side-numbers-formats`

## Monochrome diffs at night

Symptom: night diffs render monochrome.

- Themes come from `bat`; list with `show-syntax-themes`, preview `dark` (pair `dd-p07`).
- prints: `theme PASS bat-themes-dark`

## Raw markers and monochrome blame

Symptom: conflicts render raw and blame is monochrome.

- Set conflictStyle `zdiff3`; `blame` gains `hyperlinks` plus syntax highlighting (pair `dd-p08`).
- prints: `blame PASS conflict-blame-links`
