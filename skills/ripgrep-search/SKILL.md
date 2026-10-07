---
name: ripgrep-search
description: Use when searching code with ripgrep and precision matters: literal versus regex patterns, recursive directory scoping, gitignore plus hidden plus binary filtering, glob and file-type narrowing, or a persistent config file, with the exact flags to type.
version: 0.1.0
author: skillworks
license: MIT
---

# ripgrep search precision

Fix-first rules distilled from BurntSushi/ripgrep at `3fce3b5b` (master, pushed 2026-08-04) for the edit-miss class: search first with the exact scoping flags, so the lines you edit match on the first attempt. Each rule names the exact token to type. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`.

## Literal versus regex

- Treat the pattern as a regex by default: escape a regex mark with a backslash (`\(` finds a literal open parenthesis) or pass `-F` (`--fixed-strings`) to match the literal text; both forms print the same lines [src: GUIDE.md Basics plus Recursive search]

## Recursive scope

- Search the current directory by default (`rg foo` equals `rg foo ./` and descends the whole tree) and pass the directory to narrow it (`rg 'fn write\(' src` searches only `src`) [src: GUIDE.md Recursive search]

## Automatic filtering

- Expect four skips on directory search: ignore-file globs (`.gitignore`, `.ignore`, `.rgignore`), hidden files, binary files (any file holding a `NUL` byte), and symlinks, which stay unfollowed [src: GUIDE.md Automatic filtering]
- Reverse each skip on purpose: `--no-ignore` for ignore files, `--hidden` for dotfiles, `--text` for binary, `--follow` for symlinks; stack `-u` once per layer (`-u` drops ignore rules, `-uu` adds hidden, `-uuu` adds binary) and run `--debug` while still perplexed [src: GUIDE.md Automatic filtering]

## Glob narrowing

- Quote every `-g` glob in single quotes so the shell passes `*` through unexpanded (`rg lexopt -g '*.toml'` limits hits to TOML files); a leading `!` on the command line blacklists (`-g '!*.toml'`), while the same `!` whitelists inside ignore files, so read this `!` negation carefully in each place [src: GUIDE.md Manual filtering: globs]
- Stack globs with order in mind: later globs override earlier ones, so `-g '!*.toml' -g '*.toml'` searches only TOML while the reversed order can match nothing at all [src: GUIDE.md Manual filtering: globs]

## File-type narrowing

- List types with `--type-list`, include with `-t` (`--type rust`), exclude with `-T` (`--type-not rust`); add one ad-hoc type with `--type-add 'web:*.{html,css,js}'`, which lives for that command only unless stored in an alias or the config file [src: GUIDE.md Manual filtering: file types]
- Search every known type at once with `--type all` and invert it with `--type-not all`; both skip extensionless files, so an extensionless shell script stays out while its `.bash` library matches [src: GUIDE.md The special all file type]

## Config file

- Point `RIPGREP_CONFIG_PATH` at the config file (ripgrep searches no directory on its own); write one shell argument per line handed over verbatim, `#` starts a comment, flag values join with `=` (`--max-columns=150`) or sit on the next line, never `--flag value` on one line; later command-line flags override the file and `--no-config` opts out [src: GUIDE.md Configuration file]

## Encoding, archives, multiline, fancy patterns

- Read Latin-1 logs with `--encoding`, compressed files with `--search-zip` (gzip, bzip2, xz, lzma, lz4, brotli, zstd; archive formats stay skipped), line-spanning matches with `--multiline`, lookaround and backreferences with `--pcre2`; the PCRE2 engine costs speed (backtracking instead of the default finite automaton) [src: GUIDE.md File encoding plus FAQ.md compressed plus multiline plus fancy]

## Replacements

- Preview swaps with `--replace` (`-r`): only the matched text in the output changes, so `rg fast README.md -r FAST` prints `FASTer` while the files stay untouched; match the whole line or add `--only-matching` for line-shaped output, cite captures as `$1` or `$word`, and pipe `rg foo --files-with-matches` into `xargs sed` when the files themselves must change [src: GUIDE.md Replacements plus FAQ.md search-and-replace]

## Stable output

- Sort with `--sort path` for a consistent order (this pauses parallelism), ignore case with `-i`, let the case decide with `-S` (`--smart-case`), count lines with `-c`, and list searchable files with `--files` before running [src: GUIDE.md Common options plus FAQ.md order]

## Prove the pin

Replayed live 2026-10-07 with the installed `rg` (each replay ends exit 0):

```
rg -n -F "fn write(" work/ripgrep-search/src/GUIDE.md
```

prints 15 match lines: the first two are `131:469:    fn write(&mut self, buf: &[u8]) {` and `134:227:    fn write(&mut self, b: &[u8]) -> io::Result<usize> {`, and the escaped form `rg -n "fn write\("` prints the same 15. The glob-scoped `rg -n --glob "*.md" "configuration file" work/ripgrep-search/src/` hits GUIDE.md (and FAQ.md), while `rg -l --glob "*.md" "Automatic filtering" work/ripgrep-search/src/` lists 1 file: GUIDE.md. All four illustrate the Recursive search section.
