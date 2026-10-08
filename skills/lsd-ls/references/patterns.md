# Patterns: symptom to branch

Each recipe starts from a directory-listing miss the loop really makes, then names the one branch that fixes it. All replays ran on this PC on 2026-10-08.

## Bare ls habit

Symptom: the loop runs bare ls and loses colors, icons and the tree.

- Shell aliases live in the shell config: `lt` spells `lsd --tree` for the one-keystroke tree view (pair `ls-p01`).
- prints: `alias PASS tree-alias`

## Default glyph annoyance

Symptom: the loop keeps a default folder glyph it dislikes on every directory.

- Icon overrides come in 3 kinds: `filetype` changes every directory at once, plus `name` plus `extension` (pair `ls-p02`).
- prints: `icons PASS icon-kinds`

## Status-blind listing

Symptom: the loop lists files with no idea which ones changed in git.

- The `--git` flag shows status; a directory status is a `reduction` of included file statuses computed `recursively` (pair `ls-p03`).
- prints: `git PASS git-status`

## Thin default columns

Symptom: plain listing hides owners, sizes and dates the loop needs.

- The `--long` flag shows extended metadata as a `table`; `--blocks` names the blocks shown and their order (pair `ls-p04`).
- prints: `long PASS long-table`

## Flooding deep tree

Symptom: a deep node_modules tree floods the terminal.

- The `--tree` flag presents the listing as a tree; `--depth` stops it `recurs`ing past the given depth (pair `ls-p05`).
- prints: `tree PASS tree-depth`

## One fixed order

Symptom: the loop reads newest-last and cannot flip to biggest-first.

- Sort by time with `--timesort` or by size with `--sizesort`; `--reverse` flips any sort order (pair `ls-p06`).
- prints: `sort PASS sort-order`

## Default config touched

Symptom: the loop edits the live config to try a theme and cannot go back.

- Point at a trial file with `--config-file`; the Unix default sits under `XDG_CONFIG_HOME` at `.config/lsd` (pair `ls-p07`).
- prints: `cfg PASS config-path`

## Broken glyphs and colors

Symptom: the first character trims and custom colors do not apply.

- Isolate with `--icon never` plus `--ignore-config`; custom colors ride on `LS_COLORS` (pair `ls-p08`).
- prints: `iso PASS isolate-setup`
