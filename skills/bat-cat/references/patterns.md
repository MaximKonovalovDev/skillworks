# Patterns: symptom to branch

Each recipe starts from a paged-read miss the loop really makes, then names the one branch that fixes it. All replays ran on this PC on 2026-10-07.

## File read with an editor fear

Symptom: the loop avoids bat, fearing it rewrites files.

- bat is a `cat(1)` clone with `syntax highlighting` and `Git integration`: it only reads, never edits (pair `bt-p01`).
- prints: `bat PASS cat-clone`

## Output scrolls with no pager

Symptom: long output scrolls away with no way to page back.

- bat `pipes its own output to a pager` (example `less`); pass `--paging=never` to work like `cat` always (pair `bt-p02`).
- prints: `paging PASS pager-default`

## Styled output expected in a pipe

Symptom: highlighting vanishes when bat output is piped onward.

- On a `non-interactive terminal` bat is a `drop-in replacement for cat` printing the `plain file contents` (pair `bt-p03`).
- prints: `pipe PASS drop-in-plain`

## Grid and header where only numbers belong

Symptom: line-number views carry grid borders and headers.

- Run `bat -n` to show `line numbers` only (pair `bt-p04`).
- prints: `numbers PASS line-numbers-only`

## Wrong pager from two variables

Symptom: both PAGER and BAT_PAGER are set and bat picks the wrong one.

- `BAT_PAGER` will `override` `PAGER`; `builtin` selects the builtin pager (pair `bt-p05`).
- prints: `pager PASS bat-pager-wins`

## Pager origin guessed

Symptom: nobody can say where the pager choice came from.

- Read `PagerSource`: `EnvVarBatPager`, `EnvVarPager`, `Config`, `Default` (pair `bt-p06`).
- prints: `source PASS pager-source`

## Pager name unclassified

Symptom: a pager binary name means nothing to the reader.

- Read `PagerKind`: `Bat`, `Less`, `More`, `Most`, `Builtin`, `Unknown` (pair `bt-p07`).
- prints: `kind PASS pager-kind-known`

## Pager names mapped by hand

Symptom: hand mapping misses the builtin and self cases.

- Map with `from_bin`: `less` to `Less`, `builtin` to `Builtin`, current bat binary to `Bat` (pair `bt-p08`).
- prints: `bins PASS from-bin-maps-less-builtin`
