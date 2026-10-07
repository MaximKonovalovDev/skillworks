# Patterns: symptom to command

Each recipe starts from a miss the edit loop really makes, then names the one
command that fixes it. All commands were replayed on this PC on 2026-10-07.

## Escaped parenthesis prints wrong lines

Symptom: `rg 'fn write('` matches far more than the call sites, because `(` opens a group.

- Fix with an escape: `rg -n "fn write\(" work/ripgrep-search/src/GUIDE.md`
- Or fix with a literal: `rg -n -F "fn write(" work/ripgrep-search/src/GUIDE.md`
- Both print the same 15 match lines; pick `-F` when the whole pattern is literal, escape when only one mark is special and the rest stays a regex.
- prints: 15 lines, first two `131:469:    fn write(&mut self, buf: &[u8]) {` and `134:227:    fn write(&mut self, b: &[u8]) -> io::Result<usize> {`

## Whole tree searched, wanted one folder

Symptom: `rg foo` floods results from every directory.

- Recall `rg foo` equals `rg foo ./`, then scope: `rg 'fn write\(' src`
- The scoped form prints only the `src` hits, here `src/printer.rs` line 469 in the guide example.
- prints: scoped run lists `src/printer.rs` only

## Known string returns nothing

Symptom: a string you know is on disk prints zero hits.

- Suspect the four skips in order: ignore files, hidden files, `NUL`-byte binary, symlinks.
- Reverse one layer at a time: `--no-ignore`, `--hidden`, `--text`, `--follow`.
- Shortcut: add `-u` (drops ignore rules), `-uu` (adds hidden), `-uuu` (adds binary); run `--debug` while still perplexed.
- prints: `--debug` names the config file loaded and the arguments read from it

## Dependency hits drowned in noise

Symptom: `rg lexopt` buries the one Cargo line in pages of hits.

- Narrow to TOML: `rg lexopt -g '*.toml'` (single quotes keep `*` from the shell).
- Invert it: `rg lexopt -g '!*.toml'` (the `!` blacklists here).
- prints: `Cargo.toml` line 57 `lexopt = "0.3.0"` in the guide example

## Same glob typed every day

Symptom: `-g '*.rs'` retyped on every search.

- Name it once per command: `rg --type-add 'web:*.{html,css,js}' -tweb title`
- List what exists: `rg --type-list`; invert a type: `rg lexopt --type-not rust`
- Persist via alias or `RIPGREP_CONFIG_PATH`, since `--type-add` lasts one command.
- prints: `--type-list` shows the new `web` type in that command

## Every-type search skips a script

Symptom: `--type all` misses an extensionless shell script.

- That is by design: type globs match extensions, so the extensionless file matches no type while `my-shell-library.bash` matches.
- Use `--type-not all` for the inverse set.
- prints: `--type all` lists the `.bash` library only

## Flags wanted on every run

Symptom: `--hidden --smart-case --max-columns` retyped constantly.

- Write them into the file named by `RIPGREP_CONFIG_PATH`, one shell argument per line, verbatim, `#` for comments.
- Valued flags join with `=`: `--max-columns=150` (or flag and value on two lines, never `--max-columns 150` on one line).
- Override for one run on the command line (`--max-columns 0` wins because the file is prepended); opt out fully with `--no-config`.
- prints: configured run caps lines at 150 columns

## Latin-1 log, zipped dump, cross-line pattern, lookaround

Symptom: four searches that plain `rg pattern` cannot answer.

- Latin-1 bytes: `--encoding`; compressed files: `--search-zip`; cross-line: `--multiline`; lookaround or backreferences: `--pcre2` (expect slower: backtracking, not the default finite automaton).
- prints: `rg -P '(\w{10})\1'` finds the palindrome line in the FAQ example

## Preview a swap without touching files

Symptom: want to see `fast` as `FAST` in results, files unchanged.

- `rg fast README.md --replace FAST` (or `-r FAST`): only matched text in the output changes, `FASTer` included.
- Whole-line shape: match `^.*fast.*$` or add `--only-matching`; captures via `$1` or `$word`.
- Real file edits stay outside ripgrep: `rg foo --files-with-matches | xargs sed -i 's/foo/bar/g'`.
- prints: `FASTer` lines, files byte-identical after

## Order jumps between runs

Symptom: piped results arrive in a new order each run.

- Parallelism scrambles order; `--sort path` pins it (pauses parallelism).
- prints: two `--sort path` runs byte-identical
