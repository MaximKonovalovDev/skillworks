# Patterns: symptom to branch

Each recipe starts from a binary-read miss the loop really makes, then names the one branch that fixes it. All replays ran on this PC on 2026-10-08.

## Garbage from cat

Symptom: the loop cats a binary and gets garbage.

- hexyl is a `hex viewer`; colored output splits `NULL bytes`, `printable ASCII` and `non-ASCII` (pair `hx-p01`).
- prints: `view PASS hex-categories`

## Source install guess

Symptom: the loop guesses the source install spelling.

- Need `Rust 1.56` or newer; run `cargo install hexyl` or clone plus `cargo install --path` (pair `hx-p02`).
- prints: `inst PASS cargo-source`

## Distro install guess

Symptom: the loop uses one package spelling on every distro.

- On Ubuntu run `apt install hexyl`; older deb via `dpkg`; on Debian run `apt-get install hexyl` (pair `hx-p03`).
- prints: `apt PASS debian-install`

## Wrong colors

Symptom: the loop hardcodes hexyl colors.

- Colors come from `environment variables`; `HEXYL_COLOR_ASCII_PRINTABLE` covers printable, `HEXYL_COLOR_NULL` covers null (pair `hx-p04`).
- prints: `col PASS color-vars`

## Color spelling guess

Symptom: the loop guesses one color name.

- Use the 8 standard colors plus `bright blue`, and the `RGB hex` format like `#abcdef` (pair `hx-p05`).
- prints: `rgb PASS color-spellings`

## Default trace guess

Symptom: the loop guesses which default each category gets.

- Statics `COLOR_NULL` plus `COLOR_NONASCII` default to `BrightBlack` plus `Yellow` (pair `hx-p06`).
- prints: `stat PASS category-statics`

## Override guess

Symptom: setting HEXYL_COLOR_ASCII_PRINTABLE=blue does nothing the loop can explain.

- `init_color` builds the name with the `HEXYL_COLOR_` prefix and parses `DynColors` first (pair `hx-p07`).
- prints: `over PASS env-override`

## Licence guess

Symptom: the loop ships the slice without clearing the licence.

- Offered under `Apache-2.0` plus `MIT` `at your option` (pair `hx-p08`).
- prints: `lic PASS dual-licence`
