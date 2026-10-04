"""TS-1 fleet scanner on a fixture database (no real repo names or numbers here)."""
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import fleet_failures as ff  # noqa: E402
import finish_proof as fp  # noqa: E402

HOUR_MS = 3_600_000


def _db(path: Path) -> Path:
    db = path / "opencode.db"
    con = sqlite3.connect(db)
    con.execute("create table session (id text, directory text, agent text, time_updated integer)")
    con.execute("create table part (id text, message_id text, session_id text, time_created integer, time_updated integer, data text)")
    con.commit()
    con.close()
    return db


def _session(db: Path, sid: str, directory: Path, agent: str = "researcher") -> None:
    now = time.time() * 1000
    con = sqlite3.connect(db)
    con.execute("insert into session values (?, ?, ?, ?)", (sid, str(directory), agent, now))
    con.commit()
    con.close()


def _part(db: Path, sid: str, pid: str, tool: str, status: str, hours_ago: float,
          error: str | None = None, output: str | None = None, inp: dict | None = None) -> None:
    now = time.time() * 1000
    state: dict = {"status": status, "input": inp or {}}
    if error is not None:
        state["error"] = error
    if output is not None:
        state["output"] = output
    data = json.dumps({"type": "tool", "tool": tool, "state": state}, separators=(",", ":"))
    con = sqlite3.connect(db)
    con.execute("insert into part values (?, ?, ?, ?, ?, ?)", (pid, "m1", sid, now - hours_ago * HOUR_MS, now, data))
    con.commit()
    con.close()


def _world(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    skills = tmp_path / "me" / "skills"
    for name in ("alpha", "beta"):
        (skills / name).mkdir(parents=True)
        (skills / name / "SKILL.md").write_text(f"---\nname: {name}\n---\n", encoding="utf-8")
    own = tmp_path / "me"
    (own / ".git").mkdir()
    monkeypatch.setattr(fp, "SKILLS", skills)
    monkeypatch.setattr(fp, "ROOT", own)
    monkeypatch.setenv("EMPIRE_JSON", str(tmp_path / "missing-empire.json"))
    db = _db(tmp_path)
    _session(db, "s1", tmp_path / "elsewhere")
    for i in range(3):
        _part(db, "s1", f"g{i}", "github_get_file_contents", "error", 2,
              error="Failed to get file contents. The path does not point to a file 12345")
    for i in range(2):
        _part(db, "s1", f"d{i}", "deepwiki_ask_wiki_question", "error", 2,
              error="Error processing question: Repository not found abcdef1234567")
    _part(db, "s1", "w0", "bash", "completed", 2,
          output="The term 'grep' is not recognized as a name of a cmdlet381042",
          inp={"command": "grep foo bar"})
    _part(db, "s1", "old", "github_get_file_contents", "error", 70,
          error="Failed to get file contents. The path does not point to a file 999")
    return db, own


def test_norm_blanks_numbers_hashes_and_paths() -> None:
    assert "123" not in ff.norm("file 12345 missing")
    assert "abcdef1234567" not in ff.norm("id abcdef1234567 here")
    assert ff.norm("a  b") == "a b"
    assert len(ff.norm("x" * 200)) <= 80


def test_scan_groups_github_deepwiki_and_wrongshell(tmp_path: Path, monkeypatch) -> None:
    db, _own = _world(tmp_path, monkeypatch)
    res = ff.scan_db(db, 48, [])
    got = {k: v["n"] for k, v in res["classes"].items()}
    gh = [v for k, v in got.items() if k.startswith("github_get_file_contents:")]
    dw = [v for k, v in got.items() if k.startswith("deepwiki_ask_wiki_question:")]
    assert sum(gh) == 3 and sum(dw) == 2  # the 70 h old row is outside the window
    assert got.get("bash pwsh: 'grep' is not a pwsh command") == 1
    assert res["families"]["pwsh"].get("other") == 1


def test_scan_cli_prints_top_five_and_writes_failures(tmp_path: Path, monkeypatch, capsys) -> None:
    db, _own = _world(tmp_path, monkeypatch)
    state = tmp_path / "state"
    monkeypatch.setenv("SKILLDOCTOR_DIR", str(state))
    import importlib
    importlib.reload(ff)
    monkeypatch.setattr(fp, "SKILLS", tmp_path / "me" / "skills")
    monkeypatch.setattr(fp, "ROOT", tmp_path / "me")
    rc = ff.main(["--db", str(db), "scan", "--hours", "48"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "github_get_file_contents" in out and "deepwiki_ask_wiki_question" in out
    doc = json.loads((state / "failures.json").read_text(encoding="utf-8"))
    assert doc["hours"] == 48 and doc["classes"]
    importlib.reload(ff)


def test_loads_shares_one_counter_with_s1_s2(tmp_path: Path, monkeypatch) -> None:
    db, own = _world(tmp_path, monkeypatch)
    other = tmp_path / "elsewhere"
    (other / ".git").mkdir(parents=True, exist_ok=True)
    _session(db, "s2", other)
    _part(db, "s2", "k0", "skill", "completed", 1, inp={"name": "alpha"})
    _part(db, "s2", "k1", "skill", "completed", 1, inp={"name": "nope"})
    totals = fp.skill_loads(db, hours=24)
    detail = ff.loads_detail(db, hours=24)
    assert totals == {"elsewhere": 1}
    assert detail == {("alpha", "elsewhere"): 1}
    assert sum(detail.values()) == sum(totals.values())


def test_compare_before_and_verdict(tmp_path: Path, monkeypatch, capsys) -> None:
    db, _own = _world(tmp_path, monkeypatch)
    state = tmp_path / "state"
    state.mkdir()
    monkeypatch.setenv("SKILLDOCTOR_DIR", str(state))
    (state / "adopted.csv").write_text(
        "date,repo,skill,status,before,after\n2026-10-03,elsewhere,git-one-branch,adopted,9,\n", encoding="utf-8")
    import importlib
    importlib.reload(ff)
    assert ff.main(["--db", str(db), "compare", "git-one-branch", "--before"]) == 0
    now = capsys.readouterr().out.strip()
    assert now.isdigit()
    assert ff.main(["--db", str(db), "compare", "git-one-branch"]) == 0
    assert "before 9 now" in capsys.readouterr().out
    assert ff.verdict_for("git-one-branch", 10, 5) == "HALVED"
    assert ff.verdict_for("git-one-branch", 10, 6) == "DOWN"
    assert ff.verdict_for("real-browser-automation", 5, 7) == "UP"
    importlib.reload(ff)


def test_lanes_tokens_stable_without_new_work(tmp_path: Path, monkeypatch, capsys) -> None:
    db, _own = _world(tmp_path, monkeypatch)
    state = tmp_path / "state"
    state.mkdir()
    monkeypatch.setenv("SKILLDOCTOR_DIR", str(state))
    import importlib
    importlib.reload(ff)
    assert ff.main(["--db", str(db), "lanes"]) == 0
    first = json.loads((state / "lanes.json").read_text(encoding="utf-8"))
    capsys.readouterr()
    assert ff.main(["--db", str(db), "lanes"]) == 0
    second = json.loads((state / "lanes.json").read_text(encoding="utf-8"))
    for lane in ("doctor", "book", "pack", "install", "product", "planner"):
        assert lane in second and "token" in second[lane]
        assert second[lane]["token"] == first[lane]["token"]
    importlib.reload(ff)


def test_round_line_check_exits_1_when_nothing_moved(tmp_path: Path, monkeypatch, capsys) -> None:
    db, _own = _world(tmp_path, monkeypatch)
    state = tmp_path / "state"
    state.mkdir()
    monkeypatch.setenv("SKILLDOCTOR_DIR", str(state))
    import importlib
    importlib.reload(ff)
    assert ff.main(["--db", str(db), "round-line"]) == 0
    assert capsys.readouterr().out.startswith("ROUND ")
    assert ff.main(["--db", str(db), "round-line", "--check"]) == 1
    importlib.reload(ff)


def test_board_add_refuses_pipe_inside_cell(tmp_path: Path) -> None:
    board = tmp_path / "board.md"
    board.write_text("| ID | Status | Scorecard row | What | Done when | Owner role | Evidence |\n"
                     "|---|---|---|---|---|---|---|\n", encoding="utf-8")
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    import board_add as ba
    assert ba.main(["--board", str(board), "--check"]) == 0
    assert ba.main(["--board", str(board), "--id", "T-1", "--status", "READY", "--scorecard", "R1",
                    "--what", "bad | cell", "--done", "d", "--owner", "builder", "--evidence", "e"]) == 1


def test_scan_exact_window_matches_metrics_entry(tmp_path: Path, monkeypatch) -> None:
    """--from/--to pins the scan to a metrics.json window (same fp, same window).

    Regression for the judge FAIL on 000-tool-sprint: the tolerance check must
    compare one fingerprint over one window, not two drifting trailing windows.
    """
    import time as _time
    db, _own = _world(tmp_path, monkeypatch)
    now_ms = _time.time() * 1000
    res = ff.scan_db(db, 48, [], from_ms=now_ms - 3 * HOUR_MS, to_ms=now_ms - 1 * HOUR_MS)
    got = {k: v["n"] for k, v in res["classes"].items()}
    assert sum(v for k, v in got.items() if k.startswith("github_get_file_contents:")) == 3
    assert sum(v for k, v in got.items() if k.startswith("deepwiki_ask_wiki_question:")) == 2
    assert res["from"] and res["to"]
    old_only = ff.scan_db(db, 48, [], from_ms=now_ms - 71 * HOUR_MS, to_ms=now_ms - 69 * HOUR_MS)
    assert sum(v["n"] for v in old_only["classes"].values()) == 1  # only the 70 h old row
    assert "from" not in ff.scan_db(db, 48, [])  # trailing mode unchanged


def test_loads_exact_window_pins_single_day(tmp_path: Path, monkeypatch) -> None:
    """loads --from/--to pins one day (same fix as scan): the 2026-10-03 sanity
    check reads one date, not a drifting trailing window."""
    import time as _time
    db, _own = _world(tmp_path, monkeypatch)
    other = tmp_path / "elsewhere"
    (other / ".git").mkdir(parents=True, exist_ok=True)
    _session(db, "s2", other)
    _part(db, "s2", "k0", "skill", "completed", 1, inp={"name": "alpha"})
    _session(db, "s3", other)
    _part(db, "s3", "k1", "skill", "completed", 70, inp={"name": "alpha"})
    import sqlite3 as _sqlite
    _con = _sqlite.connect(db)
    _con.execute("update session set time_updated = ? where id = 's2'", (_time.time() * 1000 - 2 * HOUR_MS,))
    _con.execute("update session set time_updated = ? where id = 's3'", (_time.time() * 1000 - 70 * HOUR_MS,))
    _con.commit()
    _con.close()
    now_ms = _time.time() * 1000
    day = ff.loads_detail(db, 24, from_ms=now_ms - 3 * HOUR_MS, to_ms=now_ms - 1 * HOUR_MS)
    assert day == {("alpha", "elsewhere"): 1}
    old = ff.loads_detail(db, 24, from_ms=now_ms - 71 * HOUR_MS, to_ms=now_ms - 69 * HOUR_MS)
    assert old == {("alpha", "elsewhere"): 1}  # only the 70 h old row
    assert ff.loads_detail(db, 24) == {("alpha", "elsewhere"): 1}  # trailing mode unchanged


def test_command_line_help_exits_zero() -> None:
    root = Path(__file__).resolve().parent.parent
    assert subprocess.run([sys.executable, str(root / "tools" / "fleet_failures.py"), "--help"],
                          capture_output=True, text=True).returncode == 0
    assert subprocess.run([sys.executable, str(root / "tools" / "board_add.py"), "--help"],
                          capture_output=True, text=True).returncode == 0
