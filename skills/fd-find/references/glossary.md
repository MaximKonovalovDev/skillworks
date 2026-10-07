# Glossary

- hidden: dot files and dot directories; fd skips them unless `-H` (`--hidden`).
- ignore files: `.gitignore`, `.git/info/exclude`, global gitignore, `.ignore`, `.fdignore`, global fd ignore; fd obeys them unless `-I` (`--no-ignore`).
- unrestricted: `-u` (`--unrestricted`), the pair `--hidden --no-ignore`; spelled `-HI` in short flags.
- regex: the default pattern kind; `^x.*rc$` anchors a name search.
- glob: `-g` (`--glob`) pattern kind; quote in single quotes; `**` spans components only with `--full-path`.
- full-path: `-p` (`--full-path`) matches the pattern against the whole path instead of the filename.
- extension: `-e` (`--extension`) keeps one file extension; repeatable.
- type: `-t` (`--type`) keeps one filetype: `f` file, `d` directory, `l` symlink, `x` executable, `e` empty, plus socket, pipe, block and char devices.
- smart case: lowercase pattern searches case-insensitively, any uppercase letter flips to case-sensitive; `-s` forces sensitive, `-i` forces insensitive.
- exec: `-x` (`--exec`) runs the command once per result, in parallel.
- exec-batch: `-X` (`--exec-batch`) runs the command once with all results as arguments.
- placeholder: `{}` path, `{.}` extensionless path, `{/}` basename, `{//}` parent, `{/.}` extensionless basename.
- exclude: `-E` (`--exclude`) prunes glob-matching entries before descent; pruned directories are never entered.
- root: the positional path argument (`fd pattern path`); bare `fd pattern` uses the current directory recursively.
- catch-all: `.` or `^` as the pattern to list every entry under a directory.
