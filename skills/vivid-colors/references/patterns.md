# Patterns: symptom to branch

Each recipe starts from a color-theme miss the loop really makes, then names the one branch that fixes it. All replays ran on this PC on 2026-10-08.

## New-ls confusion

Symptom: the loop treats vivid as a new ls instead of a theme source.

- vivid is a `generator` for the `LS_COLORS` variable consumed by `ls` plus `fd` plus `tree` (pair `vc-p01`).
- prints: `gen PASS ls-colors-generator`

## Hand-edited shell RC

Symptom: the loop hand-edits colors into the shell RC instead of calling generate.

- The bash line is `export LS_COLORS="$(vivid generate molokai)"` placed in `bashrc` (pair `vc-p02`).
- prints: `bash PASS bash-export`

## Bash line pasted into fish

Symptom: the loop pastes the bash export line into fish and it is ignored.

- The fish line is `set -gx LS_COLORS (vivid generate molokai)` since fish has no `export` (pair `vc-p03`).
- prints: `fish PASS fish-setup`

## Truecolor codes on an old terminal

Symptom: an old terminal shows broken colors from 24-bit codes.

- Old terminals fall back with `--color-mode 8-bit` (`-m 8-bit`) over the `truecolor` default (pair `vc-p04`).
- prints: `bit PASS eight-bit-fallback`

## One hardcoded palette

Symptom: the loop hardcodes one palette and it clashes with light/dark switching.

- The `ansi` theme reuses the terminal `16-color` palette so ls follows the `terminal theme` (pair `vc-p05`).
- prints: `ansi PASS terminal-palette`

## Theme edits the database

Symptom: the loop edits the filetype database to add a theme and breaks detection.

- Custom themes live in a `themes` `subfolder`, or pass an `explicit path` to generate (pair `vc-p06`).
- prints: `custom PASS theme-path`

## Pink directories

Symptom: the loop colors directories pink in molokai and cannot tell links apart.

- In molokai the `directory` entry is `cyan` and the `symlink` entry is `pink` under `core` (pair `vc-p07`).
- prints: `molokai PASS dir-symlink`

## Raw escapes in one file

Symptom: the loop writes raw ANSI escapes and keeps extensions plus themes in one file.

- Colors use `RRGGBB` translated to `24-bit` or 8-bit codes, unlike `dircolors` one-file mixing (pair `vc-p08`).
- prints: `spec PASS color-spec`
