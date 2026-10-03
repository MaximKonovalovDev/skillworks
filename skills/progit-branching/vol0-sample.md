# progit-branching — Vol 0 free sample

Free sample of the `progit-branching` skill pack. Share freely; the full pack
(`SKILL.md` + `cheatsheet.md` + `glossary.md` + `patterns.md` +
`chapters/notes.md`) is the paid Vol 1 ($10, 0 sales so far).

## Try this (from the cheatsheet)

1. `git branch iss53` — create a branch (pointer move, no files change).
2. `git checkout iss53` / `git switch iss53` — HEAD now points at `iss53`.
3. Work, `git commit -a -m '...'` — `iss53` advances, `master` stays.
4. `git checkout master && git merge iss53` — fast-forward or merge commit.
5. `git branch -d iss53` — delete the merged branch.

Stuck on a conflict? `git status` lists unmerged files; resolve, then commit.

Source: Pro Git ch.3 (CC BY-NC-SA 3.0). Full notes: `chapters/notes.md`.
