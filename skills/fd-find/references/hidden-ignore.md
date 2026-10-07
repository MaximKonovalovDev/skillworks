# Hidden and ignored files (fd at 14dcd92f)

What fd skips by default and the exact flags that reverse each skip.
Sources: README.md sections Hidden and ignored files, Troubleshooting; fd.1
options -H, -I, -u, --no-ignore-vcs, --no-require-git.

Hidden: fd skips dot files and dot directories. `fd -H pre-commit`
finds `.git/hooks/pre-commit.sample` while bare `fd pre-commit`
prints nothing. Override back with `--no-hidden`. Ignored files
still stay excluded when only `-H` is given.

Ignore: inside a git checkout fd respects `.gitignore`,
`.git/info/exclude`, the global gitignore, `.ignore` and
`.fdignore`, plus the global fd ignore file. `fd -I num_cpu`
finds `target/debug/deps/libnum_cpus-*.rlib` while bare
`fd num_cpu` prints nothing. Override back with `--ignore`.
`--no-ignore-vcs` keeps non-VCS ignores but drops gitignore
handling; `--no-require-git` respects gitignores even outside
a git repository; `--no-ignore-parent` drops parent-dir
gitignore rules.

Unrestricted: `-HI` combines both reversals. `-u` and
`--unrestricted` are the same pair (`--hidden --no-ignore`).
The troubleshooting rule: when a known file is missing, retry
with `fd -u` (or `fd -HI`) before anything else.

Replayed: `rg -n "no-ignore" work/fd-find/src/README.md`
prints lines 135 and 318, short flag `-I`.
