---
name: fd-find
description: Use when finding files with fd and scoping matters: hidden plus ignore filtering, glob versus regex, full-path matching, extension and type filters, smart case, exclude pruning, or exec per-file versus batched, with the exact flags to type.
version: 0.1.0
author: skillworks
license: MIT
---

# fd file-find scoping

Fix-first rules distilled from sharkdp/fd at `14dcd92f` (master, pushed 2026-10-06) for the glob and read-missing class: scope the file list before reading, so the lines you edit match on the first attempt. Each rule names the exact token to type. Detail lives in `references/hidden-ignore.md`, `references/match-scope.md` and `references/exec-exclude.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`.

## Hidden and ignored

- Search hidden entries with `fd -H pattern` (`--hidden`); hidden stays skipped by default and `--no-hidden` turns it back off [src: README.md Hidden and ignored files]
- Search ignored entries with `fd -I pattern` (`--no-ignore`); gitignore plus fdignore plus global ignore stay respected by default and `--ignore` turns it back on [src: README.md Hidden and ignored files]

## Pattern and path scope

- Match an exact filename with `fd -g 'libc.so'` (`--glob`); the default matches the filename only while `fd -p pattern` (`--full-path`) matches the whole path and `**` spans components only in full-path glob mode [src: README.md Searching for a particular file name]
- Filter by extension with `fd -e md` plus a pattern like `fd -e rs mod`; split files from directories with `fd -t f` (`--type` file) versus `fd -t d` (directory) [src: README.md Searching for a particular file extension]
- Expect smart case by default with `fd mod`: lowercase stays case-insensitive, any uppercase letter flips to case-sensitive; force it with `fd -s` (case-sensitive) or `fd -i` (ignore-case) [src: README.md Features]

## Act on results and prune

- Run once per result with `fd -e zip -x unzip` (`--exec`) versus once for all results with `fd -g 'test_*.py' -X vim` (`--exec-batch`); name paths with `{}` (path), `{.}` (extensionless path) and `{/}` (basename) [src: README.md Command execution]
- Prune with `fd -E vendor` (`--exclude` glob); place `-E` before `-x` in the argument order and a pruned directory is never descended into [src: README.md Excluding specific files or directories]
- Pick the arity on purpose: `fd pattern` searches the current tree recursively, `fd pattern path` searches that root, bare `fd` lists everything, and `fd . dir` or `fd ^ dir` is the catch-all under one directory [src: README.md Simple search]

## Prove the pin

Replayed live 2026-10-07 with installed `rg` against `work/fd-find/src/` (each ends exit 0):

    rg -n "no-ignore" work/fd-find/src/README.md

prints 2 lines at 135 and 318, short flag `-I`. The glob form

    rg -n -- "--glob" work/fd-find/src/README.md

prints 3 lines at 117, 313 and 321, short flag `-g`. The type form

    rg -n -- "--type" work/fd-find/src/fd.1

first hits line 235, where `--type executable` implies `--type file` and `--type empty` searches files plus directories unless narrowed. The list form

    rg -l "exec-batch" work/fd-find/src/

lists 2 files: README.md and fd.1. All four illustrate the sections named above.

## Unrestricted shortcut

- Search absolutely everything with `fd -HI pattern` (hidden plus no-ignore) or `fd -u pattern` (`--unrestricted`, the same pair); re-add `--full-path` only when the pattern must span directories [src: README.md Troubleshooting fd does not find my file]
- Keep `fd -tf` (files only) in front of destructive batches like `fd -H pattern -tf -X rm -i`, and quote every glob in single quotes so the shell passes `*` through [src: README.md Deleting files]
