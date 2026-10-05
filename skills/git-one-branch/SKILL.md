---
name: git-one-branch
description: Use before any git pull, commit, push, merge or branch step in a repo that other sessions edit at the same time. One branch, pull with --no-rebase, commit only your own paths, never add -A, commit -a, rebase, amend, stash, force-push or checkout -- on files you did not write. Also covers a pull refused by dirty files, "pathspec did not match", "nothing to commit", a rejected push and index.lock. Derived from Pro Git (CC BY-NC-SA 3.0): free use and sharing only, never sold.
version: 0.1.0
license: CC-BY-NC-SA-3.0 (derived from Pro Git; free use and sharing only, never sold)
---

# git in a repo that other sessions edit

Other sessions and agent loops write in the same working folder. Their edits sit next to yours, some of them staged.
A git command that acts on everything takes their work with yours. Pro Git calls `checkout -- <file>` dangerous for the same reason: the changes are gone.
This skill is a derived work of Pro Git (CC BY-NC-SA 3.0, Scott Chacon and Ben Straub). Use it and share it free. It is never sold.

## One round, copy it
Branch: `git branch --show-current` (master in most repos, main in forge and skillworks). Stay on it.
```
git pull --no-rebase --no-edit origin master
```
Read the files again, then edit. When your work is done:
```
git status --short -- docs/a.md tools/b.mjs
git add -- tools/new-file.mjs
git commit -m "tools: add b" -m "Co-Authored-By: Name <name@example.com>" -- docs/a.md tools/b.mjs tools/new-file.mjs
git pull --no-rebase --no-edit origin master
git push origin master
```
- Paths go after `--`. Options such as `-m` go before it.
- A new file must be added first, or `git commit -- <file>` says "pathspec did not match".
- A renamed file has two paths. Commit both: `git commit -m "move" -- old.md new.md`.
- A push refused with `(fetch first)` or `(non-fast-forward)` means someone pushed first. Pull again, push again. Never force.

## Never (each one was run in a test sandbox, see references/errors.md)
- `git add -A`, `git add .`, `git commit -a`: they commit other sessions' unsaved work with yours.
- `git commit -m "..."` with no paths: it commits everything already staged, and other sessions often leave work staged.
- `git rebase`, `git pull --rebase`, `git commit --amend`, `git push --force`, `git reset --hard`: they rewrite history that others have pulled. After an amend of a pushed commit the push is rejected.
- `git stash`, `git checkout -- <file>`, `git restore <file>`, `git clean -f` on a file you did not write: they remove the other session's edit from the disk.
- Deleting `.git/index.lock` while any git command runs.

## A pull refused because of dirty files
```
error: Your local changes to the following files would be overwritten by merge:
```
What blocks a pull:
- A file changed upstream that you also changed, staged or not.
- Any STAGED file when your branch and upstream have both moved (a real merge). Unstaged edits elsewhere do not block it.
- An untracked file with the same name as an incoming file.

Steps:
1. `git status --short`. Left column = staged, right column = not staged. `git fetch origin` then `git diff --name-only HEAD origin/master` lists what the pull changes.
2. The blocking file is yours: `git commit -m "..." -- <file>`, then pull again. A text conflict: fix the markers, `git add -- <file>`, `git commit --no-edit`. Stuck: `git merge --abort` puts everything back.
3. The blocking file is not yours: do not stash, reset or checkout it. Commit your own paths and pull again later. The file's owner, or a scheduled commit job, will commit it, and then the pull works. Still refused at the end of your step: report BLOCKED with the file names.
4. Only the session that owns the repo's commits, and only for a file you can name: `git restore --staged -- <file>` takes it out of the index and leaves its content on disk. Do not do this to a staged rename.

## Other messages
- `pathspec '<file>' did not match any file(s) known to git`: the file is new, ignored or misspelled. Run `git status --short -- <file>` and `git check-ignore -v <file>`. Also seen when `-m` stands after `--`.
- `no changes added to commit` or `nothing to commit`: your paths have no change. Someone committed them. Not an error. `git log --oneline -3 -- <file>`.
- `Unable to create '.git/index.lock'`: another git command is running. `Start-Sleep 20`, try again, three times at most.
- `cannot pull with rebase: You have unstaged changes`: you used `--rebase`. Use `--no-rebase`.
- `warning: LF will be replaced by CRLF`: harmless.
- `git reflog show HEAD@{1}` fails in pwsh. Quote it: `git reflog show 'HEAD@{1}'`.

## Side branches
Work on the repo's one branch. If a session started on another branch, merge it into the main branch, push, then stop using it.
Do not delete branches by hand. Merged ones can go with `git branch -d`. `git branch -D` loses unmerged commits.
