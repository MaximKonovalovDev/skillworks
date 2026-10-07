"""adopted_after: the `after` numbers of the skill doctor's record are measured by themselves, and only from a window
that is comparable. Fixture databases are OpenCode-shaped; nothing here reads the real history except the live check."""
import csv
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

import skill_gates as g
from skill_gates import live

sys.path.insert(0, str(g.ROOT / "tools"))
import adopted_after as aa  # noqa: E402
import finish_proof as fp  # noqa: E402

HOUR = 3_600_000
NOW = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc).timestamp() * 1000
HEAD = "date,repo,skill,status,no_edit_before,no_edit_after"


# ------------------------------------------------------------------ the classes (ported from center's skill-feed scan)

def call(cmd: str, out: str = "", tool: str = "bash", repo: str = "alpha", status: str = "completed") -> list[str]:
    return aa.classify(tool, {"command": cmd}, {"output": out, "status": status}, repo)


NOT_RECOGNIZED = "The term 'grep' is not recognized as a name of a cmdlet, function, script file, or operable program."


@pytest.mark.parametrize("cmd,out,family,hits", [
    ("grep -n x f", NOT_RECOGNIZED, "pwsh", 1),
    ("for f in a b; do echo $f; done", "ParserError: Missing opening '(' after keyword 'for'.", "pwsh", 1),
    ("cat /dev/null", "Could not find a part of the path 'C:\\dev\\null'.", "pwsh", 1),
    ("date -u", "Get-Date : Parameter cannot be processed because the parameter name 'u' is ambiguous.", "pwsh", 1),
    ("ls -la", "A parameter cannot be found that matches parameter name 'la'.", "pwsh", 1),
    ("head -n 2 f", "A parameter cannot be found that matches parameter name 'n'.", "pwsh", 1),
    ("git commit -m x -- nope.txt", "error: pathspec 'nope.txt' did not match any file(s) known to git", "git", 1),
    ("git commit -m x -- a", "nothing to commit, working tree clean", "git", 1),
    ("git pull", "error: Your local changes to the following files would be overwritten by merge:", "git", 1),
    ("git pull --rebase", "error: cannot pull with rebase: You have unstaged changes.", "git", 2),  # the refusal and the --rebase itself
    ("git commit -m x", "fatal: Unable to create 'x/.git/index.lock': File exists.", "git", 1),
    ("git push origin master", " ! [rejected]        master -> master (fetch first)", "git", 1),
    ("git pull origin master", "CONFLICT (content): Merge conflict in a.txt", "git", 1),
    ("git add -A", "", "git", 1),
    ("git add .", "", "git", 1),
    ("git commit -a -m x", "", "git", 1),
    ("git commit --all -m x", "", "git", 1),
    ("git commit -a --all -m x", "", "git", 1),  # one class, however many patterns match
    ("git commit --amend -m x", "", "git", 1),
    ("git rebase main", "", "git", 1),
    ("git push --force origin master", "", "git", 1),
    ("git reset --hard HEAD", "", "git", 1),
    ("git stash", "", "git", 1),
    ("git stash pop", "", "git", 1),
    ("git checkout -- a.txt", "", "git", 1),
    ("git restore a.txt", "", "git", 1),
    ("git clean -fd", "", "git", 1),
    ("git branch -D old", "", "git", 1),
    ("node run.mjs --headless", "", "browser", 1),
    ("npx playwright test", "", "browser", 1),
    ("npm run suites", "RuntimeException: Unknown: ChildProcess.kill on detached check with no receipt to poll", "spawn", 1),
    ("node tools/lanes.mjs | Select-Object Name", "RuntimeException: prevents you from using this specific tool call: pipe through formatting", "denied", 1),
])
def test_each_target_class_is_counted(cmd: str, out: str, family: str, hits: int) -> None:
    assert call(cmd, out) == [family] * hits


@pytest.mark.parametrize("cmd,out", [
    ("git stash list", ""),
    ("git stash show", ""),
    ("git restore --staged a.txt", ""),
    ("git status --short", " M a.txt"),
    ("git push origin master", "Everything up-to-date"),
    ("Get-Content notes.txt -TotalCount 2", "line"),
    ("node -e 'console.log(1)'", "1"),
    ("echo nothing to commit", "nothing to commit"),  # the words come from echo, but git is not in the command
])
def test_ordinary_calls_are_not_counted(cmd: str, out: str) -> None:
    assert call(cmd, out) == []


def test_only_shell_calls_count_for_pwsh_git_and_browser_and_bevy_counts_in_engine2040_only() -> None:
    assert call("grep x", NOT_RECOGNIZED, tool="read") == []
    assert aa.classify("read", {"filePath": "a/bevy/mod.rs"}, {}, "engine2040") == ["bevy"]
    assert aa.classify("edit", {"filePath": "Cargo.toml", "newString": "bevy = 0.19"}, {}, "engine2040") == ["bevy"]
    assert aa.classify("read", {"filePath": "a/bevy/mod.rs"}, {}, "forge") == []
    assert aa.classify("bash", {"command": "cargo build -p bevy"}, {"output": ""}, "engine2040") == ["bevy"]


def test_a_call_that_hits_two_classes_counts_twice_and_the_error_text_may_carry_colour() -> None:
    both = "\x1b[31m" + NOT_RECOGNIZED + "\x1b[0m\nParserError: x"
    assert call("grep x", both) == ["pwsh", "pwsh"]
    assert aa.classify("bash", {"command": "grep x"}, {"error": NOT_RECOGNIZED}, "alpha") == ["pwsh"], "the error field is read when there is no output"


KILL = "RuntimeException: Unknown: ChildProcess.kill on detached check with no receipt to poll"
DENIED = "RuntimeException: prevents you from using this specific tool call: pipe through formatting"


def test_spawn_kills_and_policy_denials_count_per_repo() -> None:
    """The two 2026-10-06 classes: spawn kills after long foreground calls, denials after a pipe or shell git reach."""
    assert aa.FAMILY["bash-spawn-guard"] == "spawn" and aa.FAMILY["bash-allowlist"] == "denied"
    assert call("npm run suites", KILL) == ["spawn"]
    assert call("node tools/lanes.mjs | Select-Object Name", DENIED) == ["denied"]
    assert aa.classify("read", {"filePath": "notes.txt"}, {"output": KILL}, "alpha") == []
    assert aa.classify("read", {"filePath": "notes.txt"}, {"output": DENIED}, "alpha") == []
    assert aa.classify("bash", {"command": "x"}, {"error": KILL}, "alpha") == ["spawn"], "the error field is read when there is no output"
    assert aa.verdict("bash-spawn-guard", 66, 30) == "HALVED" and aa.verdict("bash-allowlist", 260, 130) == "HALVED"


def test_spawn_kills_and_policy_denials_count_per_repo_in_history(world: "World") -> None:
    end = datetime(2026, 10, 2, 0, 0, tzinfo=timezone.utc).timestamp() * 1000
    world.busy("alpha", end, hours=48, per_hour=20)
    world.busy("beta", end, hours=48, per_hour=20)
    world.busy("alpha", NOW, hours=40, per_hour=20)
    world.busy("beta", NOW, hours=40, per_hour=20)
    world.shell("alpha", NOW - HOUR, cmd="npm run suites", out=KILL, count=3)
    world.shell("beta", NOW - HOUR, cmd="node tools/lanes.mjs | Select-Object Name", out=DENIED, count=5)
    counts = aa.class_counts(world.db, aa.repo_dirs(world.empire), NOW - 48 * HOUR, NOW)
    assert counts["spawn"] == {"alpha": 3}
    assert counts["denied"] == {"beta": 5}


# ------------------------------------------------------------------ the record, the windows and the guard

class World:
    """An OpenCode-shaped database, a center-shaped repo list and an adopted.csv, all in a scratch folder."""

    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.db = tmp / "opencode.db"
        self.empire = tmp / "empire.json"
        self.csv = tmp / "state" / "adopted.csv"
        self.csv.parent.mkdir()
        con = sqlite3.connect(self.db)
        con.execute("create table session (id text, directory text, time_updated integer)")
        con.execute("create table part (session_id text, time_created integer, data text)")
        con.commit()
        con.close()
        self.dirs = {"alpha": tmp / "work" / "alpha", "beta": tmp / "work" / "beta"}
        self.empire.write_text(json.dumps({"repos": {k: {"dir": str(v)} for k, v in self.dirs.items()}}), encoding="utf-8")
        self.n = 0

    def shell(self, repo: str, at_ms: float, cmd: str = "dir", out: str = "", count: int = 1) -> None:
        con = sqlite3.connect(self.db)
        self.n += 1
        sid = f"s-{repo}-{self.n}"
        con.execute("insert into session values (?, ?, ?)", (sid, str(self.dirs[repo]), at_ms + 1))
        data = json.dumps({"type": "tool", "tool": "bash", "state": {"input": {"command": cmd}, "output": out}})
        con.executemany("insert into part values (?, ?, ?)", [(sid, at_ms - i, data) for i in range(count)])
        con.commit()
        con.close()

    def busy(self, repo: str, end_ms: float, hours: int, per_hour: int = 20, bad_per_hour: int = 0) -> None:
        """per_hour shell calls in each of the `hours` hours before end_ms; bad_per_hour of them are pwsh failures."""
        for h in range(hours):
            at = end_ms - h * HOUR - HOUR / 2
            self.shell(repo, at, count=per_hour)
            if bad_per_hour:
                self.shell(repo, at, cmd="grep -n x f", out=NOT_RECOGNIZED, count=bad_per_hour)

    def write_csv(self, rows: list[str]) -> None:
        self.csv.write_text(HEAD + "\n" + "\n".join(rows) + "\n", encoding="utf-8")

    def cells(self) -> list[list[str]]:
        return list(csv.reader(self.csv.read_text(encoding="utf-8").splitlines()))[1:]

    def refresh(self, now_ms: float = NOW, dry_run: bool = False, log: Path | None = None):
        return aa.refresh(self.csv, self.db, self.empire, now_ms, dry_run=dry_run, log=log)


@pytest.fixture()
def world(tmp_path: Path) -> World:
    return World(tmp_path)


def test_a_row_is_not_due_before_48_hours_after_the_install(world: World) -> None:
    world.write_csv(["2026-10-09,alpha,pwsh-for-bash-writers,adopted,10,"])
    items, said = world.refresh(now_ms=datetime(2026, 10, 11, 23, 0, tzinfo=timezone.utc).timestamp() * 1000)
    assert items[0]["due"] is False and "not due: 48 hours after the install (2026-10-10 00:00Z) is 2026-10-12 00:00Z" in items[0]["why"]
    assert "0 after numbers filled" in said and world.cells()[0][5] == ""


def test_a_paused_loop_never_gets_its_row_filled_it_would_look_halved(world: World) -> None:
    """The failure this guard exists for: a loop that stopped counts zero errors, and zero is 'fell by half'."""
    world.write_csv(["2026-10-01,alpha,pwsh-for-bash-writers,adopted,10,"])
    world.busy("alpha", datetime(2026, 10, 2, 0, 0, tzinfo=timezone.utc).timestamp() * 1000, hours=48, per_hour=20, bad_per_hour=0)  # the before window
    items, said = world.refresh()
    assert items[0]["due"] is True and items[0]["value"] is None
    assert "alpha ran in 0 of the last 48 hours, needs 36" in items[0]["why"]
    assert world.cells()[0][5] == "" and "1 due rows wait for a comparable window" in said


def test_a_few_busy_hours_do_not_pass_for_a_full_run(world: World) -> None:
    world.write_csv(["2026-10-01,alpha,pwsh-for-bash-writers,adopted,10,"])
    world.busy("alpha", datetime(2026, 10, 2, 0, 0, tzinfo=timezone.utc).timestamp() * 1000, hours=48, per_hour=20)
    world.busy("alpha", NOW, hours=10, per_hour=200)  # 2000 shell calls, but in 10 of 48 hours
    items, _ = world.refresh()
    assert items[0]["value"] is None and "ran in 10 of the last 48 hours" in items[0]["why"]


def test_an_idle_loop_with_every_hour_covered_but_few_calls_waits(world: World) -> None:
    world.write_csv(["2026-10-01,alpha,pwsh-for-bash-writers,adopted,10,"])
    world.busy("alpha", datetime(2026, 10, 2, 0, 0, tzinfo=timezone.utc).timestamp() * 1000, hours=48, per_hour=100)  # 4800 before
    world.busy("alpha", NOW, hours=48, per_hour=10)  # 480 after: under half of 4800
    items, _ = world.refresh()
    assert items[0]["value"] is None and "made 480 shell calls in the last 48 h, needs 2400" in items[0]["why"]


def test_a_full_run_fills_the_number_scaled_to_the_before_workload(world: World) -> None:
    world.write_csv(["2026-10-01,alpha,pwsh-for-bash-writers,adopted,10,", "2026-10-01,beta,git-one-branch,adopted,6,"])
    end = datetime(2026, 10, 2, 0, 0, tzinfo=timezone.utc).timestamp() * 1000
    world.busy("alpha", end, hours=48, per_hour=20)    # before: 960 shell calls
    world.busy("beta", end, hours=48, per_hour=20)
    world.busy("alpha", NOW, hours=40, per_hour=48, bad_per_hour=2)  # after: 40 x 50 = 2000 shell calls, 80 pwsh failures
    world.busy("beta", NOW, hours=40, per_hour=25)
    log = world.tmp / "state" / "after-log.jsonl"
    items, said = world.refresh(log=log)
    alpha = items[0]
    assert (alpha["raw"], alpha["before_shell"], alpha["after_shell"], alpha["active_hours"]) == (80, 960, 2000, 40)
    assert alpha["value"] == round(80 * 960 / 2000) == 38 and alpha["verdict"] == "UP"  # 10 -> 38 per the same workload: more failures, not fewer
    assert items[1]["value"] == 0 and items[1]["verdict"] == "HALVED"  # beta ran, and made no git failure at all
    assert [r[5] for r in world.cells()] == ["38", "0"]
    assert said.startswith("2 after numbers filled")
    logged = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert logged[0]["raw"] == 80 and logged[0]["value"] == 38 and logged[0]["at"] == "2026-10-10T12:00Z"


def test_the_install_moment_in_adopted_meta_json_replaces_the_end_of_the_day(world: World) -> None:
    world.write_csv(["2026-10-01,alpha,pwsh-for-bash-writers,adopted,10,"])
    (world.tmp / "state" / "adopted-meta.json").write_text(json.dumps({"2026-10-01": "2026-10-01T18:00:00Z"}), encoding="utf-8")
    items, _ = world.refresh(now_ms=datetime(2026, 10, 3, 17, 59, tzinfo=timezone.utc).timestamp() * 1000)
    assert items[0]["due"] is False and "install (2026-10-01 18:00Z) is 2026-10-03 18:00Z" in items[0]["why"]
    items, _ = world.refresh(now_ms=datetime(2026, 10, 3, 18, 1, tzinfo=timezone.utc).timestamp() * 1000)
    assert items[0]["due"] is True


def test_only_adopted_rows_without_an_after_number_are_touched_and_the_rest_stays_as_it_was(world: World) -> None:
    end = datetime(2026, 10, 2, 0, 0, tzinfo=timezone.utc).timestamp() * 1000
    world.busy("alpha", end, hours=48, per_hour=20)
    world.busy("alpha", NOW, hours=40, per_hour=20)
    rows = ["2026-10-01,alpha,pwsh-for-bash-writers,adopted,10,",
            "2026-10-01,alpha,git-one-branch,adopted,6,5",           # already measured
            "2026-10-01,alpha,real-browser-automation,proposed,7,",  # only proposed
            "2026-10-01,alpha,not-a-fleet-skill,adopted,1,"]         # unknown skill
    world.write_csv(rows)
    items, _ = world.refresh()
    got = world.cells()
    assert got[0][5] == "0" and got[1][5] == "5" and got[2][5] == "" and got[3][5] == ""
    assert [r[:5] for r in got] == [r.split(",")[:5] for r in rows]
    assert (world.csv.read_text(encoding="utf-8").splitlines()[0]) == HEAD
    assert [it["skill"] for it in items] == ["pwsh-for-bash-writers", "not-a-fleet-skill"]
    assert not [p for p in (world.tmp / "state").iterdir() if p.name.endswith(".tmp")], "the file is replaced atomically, no scratch file left"


def test_a_dry_run_measures_and_prints_but_writes_nothing(world: World) -> None:
    end = datetime(2026, 10, 2, 0, 0, tzinfo=timezone.utc).timestamp() * 1000
    world.busy("alpha", end, hours=48, per_hour=20)
    world.busy("alpha", NOW, hours=40, per_hour=20)
    world.write_csv(["2026-10-01,alpha,pwsh-for-bash-writers,adopted,10,"])
    before = world.csv.read_bytes()
    log = world.tmp / "state" / "after-log.jsonl"
    items, said = world.refresh(dry_run=True, log=log)
    assert items[0]["value"] == 0 and items[0]["verdict"] == "HALVED" and "would be filled" in said
    assert world.csv.read_bytes() == before and not log.exists()


def test_use_rows_say_up_is_good() -> None:
    assert aa.verdict("real-browser-automation", 7, 12) == "UP" and aa.verdict("bevy-rust-ecs", 60, 20) == "DOWN"
    assert aa.verdict("pwsh-for-bash-writers", 9, 4) == "HALVED" and aa.verdict("pwsh-for-bash-writers", 9, 5) == "DOWN"
    assert aa.verdict("git-one-branch", 6, 6) == "FLAT" and aa.verdict("git-one-branch", 6, 9) == "UP"
    assert aa.verdict("git-one-branch", 0, 0) == "FLAT"


def test_a_missing_database_or_record_says_so_and_does_not_raise(world: World, tmp_path: Path) -> None:
    world.write_csv(["2026-10-01,alpha,pwsh-for-bash-writers,adopted,10,"])
    assert aa.refresh(world.csv, tmp_path / "gone.db", world.empire, NOW)[1].startswith("no opencode.db at ")
    world.csv.write_text("not,a,record\n", encoding="utf-8")
    assert aa.refresh(world.csv, world.db, world.empire, NOW)[1] == "no usable adopted.csv"


# ------------------------------------------------------------------ the finish bar S5 reads the record and measures it

def _full_run(world: World) -> None:
    end = datetime(2026, 10, 2, 0, 0, tzinfo=timezone.utc).timestamp() * 1000
    world.busy("alpha", end, hours=48, per_hour=20)
    world.busy("alpha", datetime.now(timezone.utc).timestamp() * 1000, hours=40, per_hour=20)


def test_s5_measures_the_due_rows_of_the_real_record_before_it_reads_it(world: World, monkeypatch) -> None:
    _full_run(world)
    world.write_csv(["2026-10-01,alpha,pwsh-for-bash-writers,adopted,10,"])
    monkeypatch.setenv("OPENCODE_DB", str(world.db))
    monkeypatch.setattr(aa, "EMPIRE", world.empire)
    ok, msg = fp.s5(world.csv, refresh=True)
    assert ok and "alpha/pwsh-for-bash-writers 10 -> 0" in msg and "1 of 1 adopted rows have an after number" in msg
    assert "1 after numbers filled" in msg
    assert world.cells()[0][5] == "0"


def test_s5_reads_a_file_given_to_it_as_it_is_and_never_measures_for_it(world: World, monkeypatch) -> None:
    _full_run(world)
    world.write_csv(["2026-10-01,alpha,pwsh-for-bash-writers,adopted,10,"])
    monkeypatch.setenv("OPENCODE_DB", str(world.db))
    monkeypatch.setattr(aa, "EMPIRE", world.empire)
    ok, msg = fp.s5(world.csv)
    assert not ok and "0 of 1 adopted rows have an after number" in msg and world.cells()[0][5] == ""


def test_s5_prints_a_measuring_fault_instead_of_raising(world: World, monkeypatch) -> None:
    world.write_csv(["2026-10-01,alpha,pwsh-for-bash-writers,adopted,10,"])

    def broken(*a, **k):
        raise RuntimeError("database is locked")

    monkeypatch.setattr(aa, "refresh", broken)
    ok, msg = fp.s5(world.csv, refresh=True)
    assert not ok and "after-number measuring failed: RuntimeError: database is locked" in msg


def test_a_fall_in_use_rows_is_not_a_cured_class(tmp_path: Path) -> None:
    """real-browser-automation and bevy-rust-ecs rows count use, where up is good: 7 -> 3 must not meet S5."""
    p = tmp_path / "adopted.csv"
    p.write_text(HEAD + "\n2026-10-03,fp-research,real-browser-automation,adopted,7,3\n2026-10-03,engine2040,bevy-rust-ecs,adopted,60,20\n", encoding="utf-8")
    ok, msg = fp.s5(p)
    assert not ok and "0 class(es) fell by half" in msg and "2 of 2 adopted rows have an after number" in msg
    p.write_text(p.read_text(encoding="utf-8") + "2026-10-03,forge,pwsh-for-bash-writers,adopted,9,4\n", encoding="utf-8")
    ok, msg = fp.s5(p)
    assert ok and "forge/pwsh-for-bash-writers 9 -> 4" in msg and "fp-research" not in msg.split(";")[0]


def test_the_command_line_status_prints_one_line_per_row_and_a_summary(world: World) -> None:
    world.write_csv(["2026-10-09,alpha,pwsh-for-bash-writers,adopted,10,", "2026-10-09,beta,git-one-branch,adopted,4,"])
    r = subprocess.run([sys.executable, str(g.ROOT / "tools" / "adopted_after.py"), "--status", "--csv", str(world.csv), "--db", str(world.db),
                        "--empire", str(world.empire), "--now", "2026-10-10T00:00Z"], capture_output=True, text=True, encoding="utf-8",
                       stdin=subprocess.DEVNULL, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    lines = r.stdout.strip().splitlines()
    assert len(lines) == 3 and lines[0].startswith("2026-10-09 alpha") and "not due" in lines[0]
    assert lines[-1] == "0 after numbers would be filled, 0 due rows wait for a comparable window, 2 not due yet"


# ------------------------------------------------------------------ against the real history (private, live only)

@live
def test_the_port_reproduces_the_before_numbers_center_counted_in_the_same_window() -> None:
    """Same window, same database: every `before` number of the record and the total shell calls of center's baseline."""
    base = Path("C:/Users/me/Desktop/center/sprint/notes/skill-feed-baseline-2026-10-03.json")
    if not (fp.ADOPTED.is_file() and base.is_file() and aa.EMPIRE.is_file() and fp._db_path(None).is_file()):
        pytest.skip("the private record, center's baseline or the history is not on this PC")
    doc = json.loads(base.read_text(encoding="utf-8"))
    end = datetime.fromisoformat(doc["generatedAt"].replace("Z", "+00:00")).timestamp() * 1000
    dirs = aa.repo_dirs()
    shell = aa.shell_calls(fp._db_path(None), dirs, end - 48 * HOUR, end)
    assert sum(shell.values()) == doc["bashCalls"]
    counts = aa.class_counts(fp._db_path(None), dirs, end - 48 * HOUR, end)
    for date, repo, skill, status, before, _ in aa.read_rows(fp.ADOPTED)[1:]:
        if date == "2026-10-03":
            assert str(counts[aa.FAMILY[skill]].get(repo, 0)) == before, (repo, skill)
