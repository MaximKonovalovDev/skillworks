# Vol 0: git-one-branch (free sample of Fleet Vol 1)

Licence: CC-BY-NC-SA-3.0. Derived from Pro Git by Scott Chacon and Ben Straub (progit/progit2, CC BY-NC-SA 3.0, read
2026-10-03). Use it and share it free; keep the credit; share changes under the same licence. It is never sold, and it
is not in the paid zip.

Download: `fleet-vol-1-vol0.zip`. SKILL.md is at the root of the zip, with a `NOTICE.md` that repeats the licence.

## What it fixes

Several agent sessions write in one working folder, some of their edits are staged. A git command that acts on
everything takes their work with yours. The skill gives one safe round and the fix for each error text:

- Pull with `git pull --no-rebase --no-edit origin <branch>`, commit only your own paths after `--`, then pull and push.
- `Your local changes ... would be overwritten by merge`: any staged file blocks a pull that needs a real merge.
- `pathspec '...' did not match any file(s) known to git`: the file is new, ignored or misspelled.
- `nothing to commit`, a push rejected as `(fetch first)`, a stale `index.lock`, a renamed file that needs both paths.

## How it was tested

Each claim in it was run against real git in a throwaway origin and two clones, with the exact error text recorded.
Its live proof is `references/live-proof.json` in the source repository; the paid pack carries the same kind of proof for
its three skills.
