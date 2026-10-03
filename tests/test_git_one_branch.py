"""git-one-branch: every claim in the skill is run against real git in a throwaway origin and two clones.

Clone `a` is the session that reads the skill. Clone `b` plays another session that pushes to the same branch.
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import skill_gates as g
from skill_gates import live

SKILL = g.SKILLS / "git-one-branch"
pytestmark = [
    pytest.mark.skipif(not (SKILL / "SKILL.md").is_file(), reason="skill not built yet"),
    pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed"),
]

ENV = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0", LC_ALL="C", GIT_EDITOR="true")
BASE = ["git", "-c", "core.autocrlf=false", "-c", "user.name=tester", "-c", "user.email=tester@example.com"]


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([*BASE, *args], cwd=cwd, env=ENV, capture_output=True, text=True)


def out(r: subprocess.CompletedProcess) -> str:
    return r.stdout + r.stderr


class Box:
    def __init__(self, root: Path) -> None:
        self.origin = root / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "master", str(self.origin)], env=ENV, check=True)
        self.a, self.b = root / "a", root / "b"
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.a)], env=ENV, capture_output=True, check=True)
        for n in ("a.txt", "b.txt", "c.txt", "d.txt"):
            (self.a / n).write_text("".join(f"{n} line {i}\n" for i in range(1, 8)), encoding="utf-8")
        git(self.a, "add", "--", "a.txt", "b.txt", "c.txt", "d.txt")
        git(self.a, "commit", "-q", "-m", "init")
        git(self.a, "push", "-q", "origin", "master")
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.b)], env=ENV, capture_output=True, check=True)

    def other_session_pushes(self, name: str, text: str) -> None:
        git(self.b, "pull", "-q", "--no-rebase", "--no-edit", "origin", "master")
        (self.b / name).write_text(text, encoding="utf-8")
        git(self.b, "add", "--", name)
        assert git(self.b, "commit", "-q", "-m", f"other {name}", "--", name).returncode == 0
        assert git(self.b, "push", "-q", "origin", "master").returncode == 0

    def local_commit(self, name: str, text: str) -> str:
        (self.a / name).write_text(text, encoding="utf-8")
        assert git(self.a, "commit", "-q", "-m", f"mine {name}", "--", name).returncode == 0
        return git(self.a, "rev-parse", "HEAD").stdout.strip()

    def pull(self) -> subprocess.CompletedProcess:
        return git(self.a, "pull", "--no-rebase", "--no-edit", "origin", "master")

    def status(self) -> str:
        return git(self.a, "status", "--short").stdout


@pytest.fixture()
def box(tmp_path: Path) -> Box:
    return Box(tmp_path)


@live
def test_pull_refused_when_a_dirty_file_is_also_changed_upstream(box: Box) -> None:
    box.other_session_pushes("a.txt", "".join(f"a.txt line {i}\n" for i in range(1, 7)) + "a.txt line 7 FROM OTHER\n")
    (box.a / "a.txt").write_text("a.txt line 1 FROM ME\n" + "".join(f"a.txt line {i}\n" for i in range(2, 8)), encoding="utf-8")
    r = box.pull()
    assert r.returncode != 0
    assert "Your local changes to the following files would be overwritten by merge" in out(r) and "a.txt" in out(r)
    # step 2 of the skill: it is my file, commit it by path, then pull again: a clean merge, both edits survive
    assert git(box.a, "commit", "-m", "mine", "--", "a.txt").returncode == 0
    assert box.pull().returncode == 0
    text = (box.a / "a.txt").read_text(encoding="utf-8")
    assert "FROM ME" in text and "FROM OTHER" in text


@live
def test_unstaged_edits_elsewhere_do_not_block_a_real_merge(box: Box) -> None:
    box.other_session_pushes("a.txt", "other\n")
    box.local_commit("c.txt", "mine\n")
    (box.a / "d.txt").write_text("dirty, not staged\n", encoding="utf-8")
    assert box.pull().returncode == 0
    assert box.status().strip() == "M d.txt"


@live
def test_any_staged_file_blocks_a_real_merge_but_not_a_fast_forward(box: Box) -> None:
    box.other_session_pushes("a.txt", "other\n")
    (box.a / "d.txt").write_text("staged by someone\n", encoding="utf-8")
    git(box.a, "add", "--", "d.txt")
    assert box.pull().returncode == 0, "fast-forward with an unrelated staged file works"
    box.other_session_pushes("b.txt", "other again\n")
    box.local_commit("c.txt", "mine\n")  # now both sides have moved: a real merge
    # commit by path leaves d.txt staged
    assert "M  d.txt" in box.status()
    r = box.pull()
    assert r.returncode != 0 and "would be overwritten by merge" in out(r) and "d.txt" in out(r), out(r)
    # step 4 (lead only): unstage, content stays on disk, the merge goes through
    assert git(box.a, "restore", "--staged", "--", "d.txt").returncode == 0
    assert (box.a / "d.txt").read_text(encoding="utf-8") == "staged by someone\n"
    assert box.pull().returncode == 0
    assert (box.a / "d.txt").read_text(encoding="utf-8") == "staged by someone\n"


@live
def test_untracked_file_with_an_incoming_name_blocks_the_pull(box: Box) -> None:
    box.other_session_pushes("u.txt", "from other\n")
    (box.a / "u.txt").write_text("untracked here\n", encoding="utf-8")
    r = box.pull()
    assert r.returncode != 0 and "untracked working tree files would be overwritten by merge" in out(r)


@live
def test_conflict_can_be_aborted_or_finished(box: Box) -> None:
    box.other_session_pushes("a.txt", "other version\n")
    box.local_commit("a.txt", "my version\n")
    r = box.pull()
    assert "CONFLICT (content)" in out(r) and box.status().startswith("UU a.txt")
    assert git(box.a, "merge", "--abort").returncode == 0
    assert (box.a / "a.txt").read_text(encoding="utf-8") == "my version\n" and box.status() == ""
    box.pull()
    (box.a / "a.txt").write_text("resolved\n", encoding="utf-8")
    git(box.a, "add", "--", "a.txt")
    assert git(box.a, "commit", "--no-edit").returncode == 0
    assert git(box.a, "push", "-q", "origin", "master").returncode == 0


@live
def test_commit_by_path_leaves_other_sessions_work_alone(box: Box) -> None:
    (box.a / "a.txt").write_text("mine\n", encoding="utf-8")
    (box.a / "b.txt").write_text("other session, not staged\n", encoding="utf-8")
    (box.a / "c.txt").write_text("other session, staged\n", encoding="utf-8")
    git(box.a, "add", "--", "c.txt")
    assert git(box.a, "commit", "-m", "mine", "--", "a.txt").returncode == 0
    assert git(box.a, "show", "--name-only", "--format=", "HEAD").stdout.split() == ["a.txt"]
    assert box.status().splitlines() == [" M b.txt", "M  c.txt"]


@live
def test_commit_all_and_a_plain_commit_sweep_in_other_work(box: Box) -> None:
    (box.a / "a.txt").write_text("mine\n", encoding="utf-8")
    (box.a / "b.txt").write_text("other session, not staged\n", encoding="utf-8")
    assert git(box.a, "commit", "-a", "-m", "mine").returncode == 0
    assert sorted(git(box.a, "show", "--name-only", "--format=", "HEAD").stdout.split()) == ["a.txt", "b.txt"]
    (box.a / "c.txt").write_text("other session, staged\n", encoding="utf-8")
    git(box.a, "add", "--", "c.txt")
    (box.a / "d.txt").write_text("mine again\n", encoding="utf-8")
    assert git(box.a, "commit", "-m", "plain").returncode == 0
    assert git(box.a, "show", "--name-only", "--format=", "HEAD").stdout.split() == ["c.txt"], "a plain commit takes the staged work and not mine"


@live
def test_pathspec_errors_and_their_fixes(box: Box) -> None:
    (box.a / "n.txt").write_text("new\n", encoding="utf-8")
    r = git(box.a, "commit", "-m", "x", "--", "n.txt")
    assert r.returncode != 0 and "did not match any file(s) known to git" in out(r)
    git(box.a, "add", "--", "n.txt")
    assert git(box.a, "commit", "-m", "x", "--", "n.txt").returncode == 0
    (box.a / "a.txt").write_text("changed\n", encoding="utf-8")
    r = git(box.a, "commit", "--", "a.txt", "-m", "x")
    assert r.returncode != 0 and "pathspec '-m' did not match" in out(r), "-m after -- is read as a path"
    (box.a / ".gitignore").write_text("ign/\n", encoding="utf-8")
    (box.a / "ign").mkdir()
    (box.a / "ign" / "f.txt").write_text("i\n", encoding="utf-8")
    r = git(box.a, "commit", "-m", "x", "--", "ign/f.txt")
    assert r.returncode != 0 and "did not match any file(s) known to git" in out(r)
    assert ".gitignore:1:ign/" in git(box.a, "check-ignore", "-v", "ign/f.txt").stdout


@live
def test_nothing_to_commit_is_not_an_error_of_yours(box: Box) -> None:
    r = git(box.a, "commit", "-m", "x", "--", "a.txt")
    assert r.returncode == 1 and re.search(r"nothing to commit|no changes added to commit", out(r))


@live
def test_a_rename_needs_both_paths(box: Box) -> None:
    git(box.a, "mv", "d.txt", "d2.txt")
    assert box.status().strip() == "R  d.txt -> d2.txt"
    assert git(box.a, "commit", "-m", "half", "--", "d2.txt").returncode == 0
    assert box.status().strip() == "D  d.txt", "committing only the new name leaves the old name's delete staged"
    git(box.a, "reset", "-q")  # sandbox only
    git(box.a, "mv", "c.txt", "c2.txt")
    assert git(box.a, "commit", "-m", "both", "--", "c.txt", "c2.txt").returncode == 0


@live
def test_a_rejected_push_is_fixed_by_a_merge_not_by_force(box: Box) -> None:
    box.other_session_pushes("b.txt", "other\n")
    mine = box.local_commit("c.txt", "mine\n")
    r = git(box.a, "push", "origin", "master")
    assert r.returncode != 0 and re.search(r"\((fetch first|non-fast-forward)\)", out(r)), out(r)
    assert box.pull().returncode == 0
    assert git(box.a, "push", "origin", "master").returncode == 0
    assert git(box.a, "rev-list", "--merges", "--count", "HEAD").stdout.strip() == "1"
    assert git(box.a, "merge-base", "--is-ancestor", mine, "HEAD").returncode == 0, "my commit kept its SHA"


@live
def test_amend_of_a_pushed_commit_is_rejected(box: Box) -> None:
    box.local_commit("c.txt", "one\n")
    assert git(box.a, "push", "-q", "origin", "master").returncode == 0
    assert git(box.a, "commit", "--amend", "-m", "one, reworded").returncode == 0
    r = git(box.a, "push", "origin", "master")
    assert r.returncode != 0 and "rejected" in out(r)


@live
def test_pull_with_rebase_refuses_a_dirty_tree(box: Box) -> None:
    box.other_session_pushes("a.txt", "other\n")
    (box.a / "b.txt").write_text("dirty\n", encoding="utf-8")
    r = git(box.a, "pull", "--rebase", "origin", "master")
    assert r.returncode != 0 and "cannot pull with rebase: You have unstaged changes" in out(r)


@live
def test_stash_and_checkout_remove_other_sessions_edits_from_disk(box: Box) -> None:
    (box.a / "b.txt").write_text("other session's unsaved work\n", encoding="utf-8")
    git(box.a, "stash")
    assert "unsaved work" not in (box.a / "b.txt").read_text(encoding="utf-8")
    git(box.a, "stash", "pop")
    assert "unsaved work" in (box.a / "b.txt").read_text(encoding="utf-8")
    git(box.a, "checkout", "--", "b.txt")
    assert "unsaved work" not in (box.a / "b.txt").read_text(encoding="utf-8")
    assert git(box.a, "stash", "list").stdout == "", "and the work is not in the stash either"


@live
def test_index_lock_blocks_every_commit_until_it_is_gone(box: Box) -> None:
    lock = box.a / ".git" / "index.lock"
    lock.write_text("", encoding="utf-8")
    (box.a / "c.txt").write_text("y\n", encoding="utf-8")
    r = git(box.a, "commit", "-m", "x", "--", "c.txt")
    assert r.returncode != 0 and "Unable to create" in out(r) and "index.lock" in out(r)
    lock.unlink()  # sandbox only: no git process runs here
    assert git(box.a, "commit", "-m", "x", "--", "c.txt").returncode == 0


@live
def test_multiple_message_flags_make_a_trailer(box: Box) -> None:
    (box.a / "c.txt").write_text("y\n", encoding="utf-8")
    assert git(box.a, "commit", "-m", "subject", "-m", "Co-Authored-By: Name <name@example.com>", "--", "c.txt").returncode == 0
    assert git(box.a, "log", "-1", "--format=%B").stdout.strip().endswith("Co-Authored-By: Name <name@example.com>")


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh 7 is not installed")
@live
def test_reflog_selector_needs_quotes_in_pwsh(box: Box) -> None:
    box.local_commit("c.txt", "one\n")
    box.local_commit("c.txt", "two\n")

    def ps(cmd: str) -> subprocess.CompletedProcess:
        return subprocess.run(["pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", cmd], cwd=box.a, env=ENV, capture_output=True, text=True)

    assert ps("git log -1 --format=%s HEAD@{1}").returncode != 0
    ok = ps("git log -1 --format=%s 'HEAD@{1}'")
    assert ok.returncode == 0 and "mine c.txt" in ok.stdout


def test_errors_md_cites_tests_that_exist() -> None:
    """Fast check: errors.md says which live test produced each message; the names must be real."""
    cited = set(re.findall(r"\b(test_\w+)\b(?!\.py)", (SKILL / "references" / "errors.md").read_text(encoding="utf-8")))
    mine = set(re.findall(r"^def (test_\w+)\(", Path(__file__).read_text(encoding="utf-8"), re.M))
    assert len(cited) >= 12
    assert cited <= mine, f"errors.md cites tests that do not exist: {sorted(cited - mine)}"
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for needle in ("would be overwritten by merge", "did not match any file(s) known to git",
                   "cannot pull with rebase: You have unstaged changes", "Unable to create", "(fetch first)"):
        assert needle in skill or needle in (SKILL / "references" / "errors.md").read_text(encoding="utf-8"), needle
