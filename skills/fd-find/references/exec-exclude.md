# Act and prune: exec, placeholders, exclude (fd at 14dcd92f)

What to run on the results and what to cut before running.
Sources: README.md sections Command execution, Excluding
specific files or directories, Deleting files; fd.1 options
-x, -X, -E, --format, -j, -l, --prune.

Exec: `-x` (`--exec`) runs the command once per result in
parallel (`fd -e zip -x unzip` unzips each archive;
`fd -e h -e cpp -x clang-format -i` formats each file).
`-X` (`--exec-batch`) launches once with all results as
arguments (`fd -g 'test_*.py' -X vim` opens one editor;
`fd -e cpp -e cxx -e h -e hpp -X rg 'std::cout'` searches
inside C++ sources; `fd -tf -X rm -i` deletes only files,
interactively). Put `-x` or `-X` last: positional args
after them belong to the command template, or terminate
with `\;`. Repeat the flag to run several commands per
file in order. `-j` (`--threads`) caps parallelism;
`--threads=1` runs serially. `-l` (`--list-details`)
is shorthand for batched `ls -lhd`. Shell aliases and
functions do not work under `-x`/`-X`; call
`fd -x bash -c 'fn "$1"' bash` instead.

Placeholders: `{}` path (`documents/images/party.jpg`),
`{.}` extensionless path (`documents/images/party`),
`{/}` basename (`party.jpg`), `{//}` parent
(`documents/images`), `{/.}` basename extensionless
(`party`). `--format` uses the same set. No placeholder
means an implicit `{}` is appended. Quote placeholders
when the shell would expand them.

Exclude: `-E` (`--exclude`) prunes by glob before
descent (`fd -H -E .git`, `fd -E '*.bak'`,
`fd -E /mnt/external-drive`). A pruned directory is
never descended into (`--prune` is the same idea for
matches). Make patterns permanent in `.fdignore`
(repo-local, gitignore syntax) or the global ignore
file (`~/.config/fd/ignore`, `%APPDATA%/fd/ignore`
on Windows). `.ignore` files are honored too.

Replayed: `rg -l "exec-batch" work/fd-find/src/`
lists 2 files: README.md and fd.1.
