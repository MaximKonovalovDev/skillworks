# Glossary

- literal: pattern text matched byte for byte; `-F` (`--fixed-strings`) forces it.
- regex: pattern text read as a regular expression (the default); `(` opens a group, `\(` matches the mark itself.
- escape: a backslash that strips the special meaning off the next mark.
- recursive: descending from the current directory through the whole tree; `rg foo` equals `rg foo ./`.
- ignore files: `.gitignore`, `.ignore`, `.rgignore` globs ripgrep obeys; `.ignore` beats `.gitignore`, `.rgignore` beats `.ignore`.
- hidden: files and directories starting with a dot; skipped unless `--hidden`.
- binary: any file holding a `NUL` byte; skipped unless `--text`.
- symlink: a link ripgrep leaves unfollowed unless `--follow`.
- glob: an ad-hoc `-g` file pattern, quoted in single quotes; leading `!` is a negation (blacklist on the command line, whitelist in ignore files); later globs override earlier ones.
- file type: a name for one or more globs (`--type rust`); `--type-list` lists them, `--type-add` defines one for a single command, `-T` (`--type-not`) excludes.
- all: the special type matching every known type at once; extensionless files match no type.
- config file: the file named by `RIPGREP_CONFIG_PATH`; one shell argument per line, handed over verbatim; command-line flags override it.
- encoding: the byte-to-text mapping (`--encoding`); ripgrep sniffs a BOM and defaults to `auto`.
- multiline: matches allowed to span lines (`--multiline`).
- PCRE2: the opt-in engine (`--pcre2`) for lookaround and backreferences; backtracking makes it slower than the default finite automaton.
- replace: output-only swap (`--replace`, `-r`) of matched text; `$1` and `$word` cite captures; files stay untouched.
