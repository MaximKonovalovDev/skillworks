## 0000
[[ch03-git-branching]]
== Git Branching

(((branches)))
Nearly every VCS has some form of branching support.
Branching means you diverge from the main line of development and continue to do work without messing with that main line.
In many VCS tools, this is a somewhat expensive process, often requiring you to create a new copy of your source code directory, which can take a long time for large projects.

Some people refer to Git's branching model as its "`killer feature,`" and it certainly sets Git apart in the VCS community.
Why is it so special?
The way Git branches is incredibly lightweigh

## 0001
 'hotfix'
$ vim index.html
$ git commit -a -m 'Fix broken email address'
[hotfix 1fb7853] Fix broken email address
 1 file changed, 2 insertions(+)
----

.Hotfix branch based on `master`
image::images/basic-branching-4.png[Hotfix branch based on `master`]

You can run your tests, make sure the hotfix is what you want, and finally merge the `hotfix` branch back into your `master` branch to deploy to production.
You do this with the `git merge` command:(((git commands, merge)))

[source,console]
----
$ git checkout master
$ git merge hotfix
Updating f42c576..3a0874c
Fast-forward
 index.html | 2 

## 0002
 hasn't automatically created a new merge commit.
It has paused the process while you resolve the conflict.
If you want to see which files are unmerged at any point after a merge conflict, you can run `git status`:

[source,console]
----
$ git status
On branch master
You have unmerged paths.
  (fix conflicts and run "git commit")

Unmerged paths:
  (use "git add <file>..." to mark resolution)

    both modified:      index.html

no changes added to commit (use "git add" and/or "git commit -a")
----

Anything that has merge conflicts and hasn't been resolved is listed as unmerged.
Git adds stan

## 0003
rent branches:

[source,console]
----
$ git branch
  iss53
* master
  testing
----

Notice the `*` character that prefixes the `master` branch: it indicates the branch that you currently have checked out (i.e., the branch that `HEAD` points to).
This means that if you commit at this point, the `master` branch will be moved forward with your new work.
To see the last commit on each branch, you can run `git branch -v`:

[source,console]
----
$ git branch -v
  iss53   93b412c Fix javascript issue
* master  7a98805 Merge branch 'iss53'
  testing 782fd34 Add scott to the author list in the readme
-

## 0004
otes/origin/main
  remotes/origin/master
----

Your local `master` branch is gone, as it's replaced with the `main` branch.
The `main` branch is present on the remote.
However, the old `master` branch is still present on the remote.
Other collaborators will continue to use the `master` branch as the base of their work, until you make some further changes.

Now you have a few more tasks in front of you to complete the transition:

* Any projects that depend on this one will need to update their code and/or configuration.
* Update any test-runner configuration files.
* Adjust build and release s

## 0005
 pointer to the local branch you're currently on.
In this case, you're still on `master`.
The `git branch` command only _created_ a new branch -- it didn't switch to that branch.

.HEAD pointing to a branch
image::images/head-to-master.png[HEAD pointing to a branch]

You can easily see this by running a simple `git log` command that shows you where the branch pointers are pointing.
This option is called `--decorate`.

[source,console]
----
$ git log --oneline --decorate
f30ab (HEAD -> master, testing) Add feature #32 - ability to add new formats to the central interface
34ac2 Fix bug #1328 - s

## 0006
t to the way most older VCS tools branch, which involves copying all of the project's files into a second directory.
This can take several seconds or even minutes, depending on the size of the project, whereas in Git the process is always instantaneous.
Also, because we're recording the parents when we commit, finding a proper merge base for merging is automatically done for us and is generally very easy to do.
These features help encourage developers to create and use branches often.

Let's see why you should do so.

[NOTE]
.Creating a new branch and switching to it at the same time
====
It's

## 0007
 on something other than the rebase target branch.
Take a history like <<rbdiag_e>>, for example.
You branched a topic branch (`server`) to add some server-side functionality to your project, and made a commit.
Then, you branched off that to make the client-side changes (`client`) and committed a few times.
Finally, you went back to your `server` branch and did a few more commits.

[[rbdiag_e]]
.A history with a topic branch off another topic branch
image::images/interesting-rebase-1.png[A history with a topic branch off another topic branch]

Suppose you decide that you want to merge your cli

## 0008
Now you're both in a pickle.
If you do a `git pull`, you'll create a merge commit which includes both lines of history, and your repository will look like this:

[[_merge_rebase_work]]
.You merge in the same work again into a new merge commit
image::images/perils-of-rebasing-4.png[You merge in the same work again into a new merge commit]

If you run a `git log` when your history looks like this, you'll see two commits that have the same author, date, and message, which will be confusing.
Furthermore, if you push this history back up to the server, you'll reintroduce all those rebased commits t

## 0009
 in the way that's best for future readers.

Now, to the question of whether merging or rebasing is better: hopefully you'll see that it's not that simple.
Git is a powerful tool, and allows you to do many things to and with your history, but every team and every project is different.
Now that you know how both of these things work, it's up to you to decide which one is best for your particular situation.

You can get the best of both worlds: rebase local changes before pushing to clean up your work, but never rebase anything that you've pushed somewhere.

[[_remote_branches]]
=== Remote Branc

## 0010
to the commit that `teamone` has as its `master` branch.

.Remote-tracking branch for `teamone/master`
image::images/remote-branches-5.png[Remote-tracking branch for `teamone/master`]

[[_pushing_branches]]
==== Pushing

(((pushing)))
When you want to share a branch with the world, you need to push it up to a remote to which you have write access.
Your local branches aren't automatically synchronized to the remotes you write to -- you have to explicitly push the branches you want to share.
That way, you can use private branches for work you don't want to share, and push up only the topic branc

## 0011
on enough operation that Git provides the `--track` shorthand:

[source,console]
----
$ git checkout --track origin/serverfix
Branch serverfix set up to track remote branch serverfix from origin.
Switched to a new branch 'serverfix'
----

In fact, this is so common that there's even a shortcut for that shortcut.
If the branch name you're trying to checkout (a) doesn't exist and (b) exactly matches a name on only one remote, Git will create a tracking branch for you:

[source,console]
----
$ git checkout serverfix
Branch serverfix set up to track remote branch serverfix from origin.
Switched to

## 0012
was accidentally deleted, it's often easy to recover.

=== Branching Workflows

Now that you have the basics of branching and merging down, what can or should you do with them?
In this section, we'll cover some common workflows that this lightweight branching makes possible, so you can decide if you would like to incorporate them into your own development cycle.

==== Long-Running Branches

(((branches, long-running)))
Because Git uses a simple three-way merge, merging from one branch into another multiple times over a long period is generally easy to do.
This means you can have several branch