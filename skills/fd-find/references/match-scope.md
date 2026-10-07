# Match scope: glob, path, extension, type, case (fd at 14dcd92f)

How fd matches patterns and narrows the list before reading.
Sources: README.md sections Simple search, Searching for a
particular file extension, Searching for a particular file name,
Matching the full path, Command-line options; fd.1 options
-g, -p, -e, -t, -s, -i, -F, --exact.

Arity: `fd netfl` searches the current directory recursively
for entries containing the pattern (regex by default).
`fd passwd /etc` searches that root instead. Bare `fd`
lists every entry recursively. `fd . fd/tests/` and
`fd ^ fd/tests/` are the catch-all forms that list all
entries under one directory.

Regex versus glob: the pattern is a regex unless `--glob`
is passed. `fd '^x.*rc$'` matches names starting with x
and ending with rc. `fd -g 'libc.so'` matches exactly
that filename. Quote every glob in single quotes so the
shell passes `*` through. `--regex` overrides `--glob`;
`-F` (`--fixed-strings`) treats the pattern as a literal
substring; `--exact` requires the whole filename to match.

Filename versus full path: fd matches the filename only.
`fd -p '.*/lesson-\d+/[a-z]+.(jpg|png)'` matches against
the full path instead, as does `fd -u -p -g '**/.git/config'`.
`**` spans multiple path components only in full-path
glob mode. Quote regexes in single quotes; when the
pattern starts with a dash, run `fd -- '-pattern'`.

Extension and type: `fd -e md` lists Markdown files;
`fd -e rs mod` combines extension with a pattern;
repeat `-e` for several extensions. `fd -t f` keeps
files, `fd -t d` keeps directories (`-tf`, `-td`
short forms), `-tl` symlinks, `-tx` executables,
`-te` empty. `--type executable` implies `--type file`
by default; `--type empty` searches empty files and
directories unless `--type file` or `--type directory`
narrows it. Stack `--type file --type symlink` to
include both.

Case: smart case is the default. Lowercase `fd mod`
matches mixed case; adding one uppercase letter flips
to case-sensitive. Force with `fd -s`
(`--case-sensitive`) or `fd -i` (`--ignore-case`).

Replayed: `rg -n -- "--glob" work/fd-find/src/README.md`
prints lines 117, 313, 321, short flag `-g`.
`rg -n -- "--type" work/fd-find/src/fd.1` first hits
line 235 with the executable/empty rule above.
