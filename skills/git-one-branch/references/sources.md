# Sources and licences (verified 2026-10-03)

- Pro Git, 2nd edition, by Scott Chacon and Ben Straub: https://github.com/progit/progit2
  - Pinned commit: a013e3230a1207cfa5ae94d28ba7d2021063c337 (main, 2026-05-25), folder `book/`.
  - Licence, read live from `LICENSE.asc` on 2026-10-03: Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported (CC-BY-NC-SA-3.0). The GitHub API reports "NOASSERTION" for it.
  - Because this skill is a derived work, it carries the same licence: credit Pro Git, no commercial use, share under the same terms. It is used inside our own repos and shared free. It is never sold, never put in a paid pack.
  - Passages checked: 02 Git Basics (recording changes, undoing things, working with remotes), 03 Git Branching (basic branching and merging, rebasing), 07 Git Tools (stashing and cleaning, rewriting history, advanced merging).
- Our own rule "one branch per repo, always": pull first, commit your own paths, push; never rebase, amend or force-push a shared branch. This is our own rule, not Pro Git text.
- Measured, not read: all messages and behaviours in `errors.md`, from git 2.53 in a sandbox (tests/test_git_one_branch.py).

## Which rule rests on which passage (paraphrased)
- Never rebase, amend or force-push shared history: Pro Git, Rebasing, "The Perils of Rebasing" says not to rebase commits that exist outside your repository and that others may have based work on. Rewriting History says an amend changes the commit's SHA and should not be used on a pushed commit.
- `checkout -- <file>` and `restore <file>` lose edits: Pro Git, Undoing Things, marks both as dangerous because the local changes are gone.
- Clean state before a merge or branch switch: Pro Git, Basic Branching and Merging, says Git will not switch when uncommitted changes conflict, and that a clean state is best.
- Merge conflict handling: Pro Git, Basic Merge Conflicts: Git pauses, `git status` lists unmerged paths, you resolve and commit.
- Stash as the textbook answer to a messy tree: Pro Git, Stashing and Cleaning. We do not use it here because the dirty files belong to other sessions. That is our own rule, not Pro Git advice.

Credit line for THIRD_PARTY_NOTICES.md: progit/progit2, Pro Git (CC BY-NC-SA 3.0). Free use and sharing only.
