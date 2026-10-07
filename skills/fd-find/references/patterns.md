# Patterns: symptom to command

Each recipe starts from a miss the file-find loop really makes, then names
the one command that fixes it. All commands replayed 2026-10-07.

## Known hook sample returns nothing

Symptom: a hook sample under a dot directory prints zero hits.

- Scope first: `fd -H pre-commit` finds `.git/hooks/pre-commit.sample`.
- prints: `.git/hooks/pre-commit.sample` under `-H`, nothing under bare `fd`.

## Build artifact missing inside a git checkout

Symptom: a build artifact that gitignore lists never appears.

- Scope first: `fd -I num_cpu` finds `target/debug/deps/libnum_cpus-*.rlib`.
- Search absolutely everything: `fd -HI pattern` or `fd -u pattern`.
- prints: `rg -n "no-ignore" work/fd-find/src/README.md` hits lines 135 and 318.

## Exact filename versus path-spanning config

Symptom: `libc.so` wanted by name, then configs under any `.git` dir.

- Exact name: `fd -g 'libc.so'`; full-path glob: `fd -u -p -g '**/.git/config'`.
- prints: `rg -n -- "--glob" work/fd-find/src/README.md` hits lines 117, 313, 321.

## Markdown by extension, directories by type

Symptom: every Markdown file with mod in the name, then only directories named target.

- `fd -e md mod` for the first; `fd -t d target` for the second.
- prints: `rg -n -- "--type" work/fd-find/src/fd.1` first hits line 235.

## Uppercase pattern suddenly narrows

Symptom: lowercase matches mixed case, uppercase stops matching lowercase.

- That is smart case; force with `fd -s` or `fd -i`.
- prints: smart-case rule in README.md Features list.

## Unzip each versus edit all at once

Symptom: unzip each archive in parallel versus one editor for all test files.

- Per result: `fd -e zip -x unzip`; batched: `fd -g 'test_*.py' -X vim`.
- Convert with placeholders: `fd -e jpg -x convert {} {.}.png`.
- prints: `rg -l "exec-batch" work/fd-find/src/` lists 2 files.

## Vendor tree drowns results

Symptom: a huge tree buries the hits.

- Prune before exec: `fd -H -E .git pattern`, `fd -E '*.bak'`.
- prints: pruned directory never descended.

## One argument, two arguments, no arguments

Symptom: unsure which arity lists what.

- `fd pattern` current tree, `fd pattern path` that root, bare `fd` everything, `fd . dir` catch-all.
- prints: arity rule in README.md Simple search.
