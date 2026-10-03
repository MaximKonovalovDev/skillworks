# Git messages in a shared folder: cause and fix

Every message below was produced by git 2.53 in a throwaway origin with two clones. The test that made it is named in brackets (tests/test_git_one_branch.py).

- `error: Your local changes to the following files would be overwritten by merge:` then a file list. The pull stopped before it changed anything.
  - The file is changed upstream and on your disk. [test_pull_refused_when_a_dirty_file_is_also_changed_upstream]
  - The file is only staged, your branch and upstream have both moved, and the file is not even in the incoming change. Any staged file blocks a real merge. A fast-forward does not care. Unstaged edits do not block. [test_any_staged_file_blocks_a_real_merge_but_not_a_fast_forward, test_unstaged_edits_elsewhere_do_not_block_a_real_merge]
  - Fix: yours, then commit by path and pull again. Not yours, then leave it and pull later.
- `Merge with strategy ort failed.` Printed after the line above on a real merge. Same causes.
- `error: The following untracked working tree files would be overwritten by merge:` an untracked file has the name of an incoming file. Not yours: leave it, pull later. Yours: move it away, pull. [test_untracked_file_with_an_incoming_name_blocks_the_pull]
- `CONFLICT (content): Merge conflict in a.txt`, status `UU a.txt`. Fix the `<<<<<<<` markers, `git add -- a.txt`, `git commit --no-edit`. Or `git merge --abort`: everything is back as before the pull. [test_conflict_can_be_aborted_or_finished]
- `error: pathspec 'n.txt' did not match any file(s) known to git`: new file not added, ignored path, or `-m` written after `--`. [test_pathspec_errors_and_their_fixes]
- `no changes added to commit (use "git add" and/or "git commit -a")`, exit 1: the paths you named have no change. [test_nothing_to_commit_is_not_an_error_of_yours]
- `! [rejected] master -> master (fetch first)` or `(non-fast-forward)`: someone pushed first. Git says `fetch first` when their commits are not in your clone yet. `git pull --no-rebase --no-edit origin master`, then push. The merge keeps your commit's SHA. [test_a_rejected_push_is_fixed_by_a_merge_not_by_force]
- After `git commit --amend` of a pushed commit the same rejection comes back, and only a force would get past it. Do not amend. [test_amend_of_a_pushed_commit_is_rejected]
- `fatal: Unable to create '.../.git/index.lock': File exists.` Another git command is running. Wait and try again. [test_index_lock_blocks_every_commit_until_it_is_gone]
- `error: cannot pull with rebase: You have unstaged changes.` You wrote `--rebase`. [test_pull_with_rebase_refuses_a_dirty_tree]
- `fatal: ambiguous argument 'HEAD@': unknown revision`: pwsh read `@{` as a hashtable. Quote `'HEAD@{1}'`. [test_reflog_selector_needs_quotes_in_pwsh]

What the dangerous commands did in the same sandbox:
- `git commit -a` committed an unstaged edit of another session. A plain `git commit -m` committed a file another session had staged and left mine out. [test_commit_all_and_a_plain_commit_sweep_in_other_work]
- `git stash` and `git checkout -- <file>` removed another session's unsaved edit from the disk; after the checkout it was in no stash either. [test_stash_and_checkout_remove_other_sessions_edits_from_disk]
- Committing only the new name of a renamed file left `D  old` staged. Name both paths. [test_a_rename_needs_both_paths]
