"""FINISH-LINE proofs: S1 and S2 (real loads), S3 (a tested pack live), S5 (a class halved), S6 (skills proven)."""
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import finish_proof as fp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HOUR_MS = 3_600_000


def _world(tmp_path: Path) -> tuple[Path, Path, Path]:
    """A skills folder with two skills, an own repo, and an OpenCode-shaped database (read-only fixture)."""
    skills = tmp_path / "me" / "skills"
    for name in ("alpha", "beta", "_template"):
        (skills / name).mkdir(parents=True)
        (skills / name / "SKILL.md").write_text(f"---\nname: {name}\n---\n", encoding="utf-8")
    own = tmp_path / "me"
    (own / ".git").mkdir()
    db = tmp_path / "opencode.db"
    con = sqlite3.connect(db)
    con.execute("create table session (id text, directory text, time_updated integer)")
    con.execute("create table part (session_id text, time_created integer, data text)")
    con.commit()
    con.close()
    return skills, own, db


def _repo(tmp_path: Path, name: str) -> Path:
    d = tmp_path / name
    (d / ".git").mkdir(parents=True)
    return d


def _load(db: Path, sid: str, directory: Path, skill: str, hours_ago: float, tool: str = "skill") -> None:
    now = time.time() * 1000
    con = sqlite3.connect(db)
    if not con.execute("select 1 from session where id = ?", (sid,)).fetchone():
        con.execute("insert into session values (?, ?, ?)", (sid, str(directory), now))
    data = json.dumps({"type": "tool", "tool": tool, "state": {"input": {"name": skill}}}, separators=(",", ":"))
    con.execute("insert into part values (?, ?, ?)", (sid, now - hours_ago * HOUR_MS, data))
    con.commit()
    con.close()


def test_loads_count_only_real_skill_calls_of_this_repo_in_other_repos(tmp_path: Path) -> None:
    skills, own, db = _world(tmp_path)
    forge, center = _repo(tmp_path, "forge"), _repo(tmp_path, "center")
    for i in range(3):
        _load(db, "s1", forge, "alpha", 1 + i)
    _load(db, "s2", center, "beta", 2)
    _load(db, "s3", own, "alpha", 1)                         # skillworks itself does not count
    _load(db, "s4", forge, "engine-code", 1)                 # a skill of another repo does not count
    _load(db, "s5", forge, "alpha", 30)                      # older than 24 h
    _load(db, "s6", forge, "alpha", 1, tool="bash")          # not a skill call
    _load(db, "s7", tmp_path / "nowhere", "alpha", 1)        # not inside a git repo
    assert fp.skill_loads(db, skills=skills, own=own) == {"forge": 3, "center": 1}


def test_a_folder_inside_a_repo_or_a_parent_with_git_is_not_a_repo(tmp_path: Path) -> None:
    skills, own, db = _world(tmp_path)
    home = _repo(tmp_path, "home")                           # a dotfiles repo above the desktop folder
    (home / "Desktop").mkdir()
    _load(db, "s1", home / "Desktop", "alpha", 1)
    assert fp.skill_loads(db, skills=skills, own=own) == {}


def test_s1_and_s2_read_the_database(tmp_path: Path, monkeypatch) -> None:
    skills, own, db = _world(tmp_path)
    monkeypatch.setattr(fp, "SKILLS", skills)
    monkeypatch.setattr(fp, "ROOT", own)
    ok, msg = fp.s1(db)
    assert not ok and "0 loads" in msg
    repos = [_repo(tmp_path, f"repo{i}") for i in range(4)]
    for i, repo in enumerate(repos):
        for j in range(3):
            _load(db, f"s{i}", repo, "alpha", 1 + j)
    ok, msg = fp.s1(db)
    assert ok and "12 loads" in msg                      # 10 loads are enough for S1 ...
    ok, msg = fp.s2(db)
    assert not ok and "4 other repos" in msg             # ... but 4 repos are not 5
    _load(db, "s9", _repo(tmp_path, "repo4"), "beta", 1)
    ok, msg = fp.s2(db)
    assert ok and "5 other repos" in msg


def test_s1_and_s2_without_a_database_are_open(tmp_path: Path) -> None:
    for bar in (fp.s1, fp.s2):
        ok, msg = bar(tmp_path / "missing.db")
        assert not ok and "no opencode.db" in msg


def _csv(tmp_path: Path, rows: list[str]) -> Path:
    p = tmp_path / "adopted.csv"
    p.write_text("date,repo,skill,status,before,after\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return p


def test_s5_needs_one_adopted_class_cut_by_half(tmp_path: Path) -> None:
    ok, msg = fp.s5(_csv(tmp_path, ["2026-10-03,forge,pwsh,adopted,9,", "2026-10-03,forge,git,adopted,6,4"]))
    assert not ok and "0 class" in msg and "1 of 2 adopted rows" in msg   # no after number, and 6 -> 4 is not half
    ok, msg = fp.s5(_csv(tmp_path, ["2026-10-03,skillworks,pwsh,adopted,10,1", "2026-10-03,forge,pwsh,proposed,10,1"]))
    assert not ok                                                          # our own repo and a proposal do not count
    ok, msg = fp.s5(_csv(tmp_path, ["2026-10-03,forge,pwsh,adopted,9,5"]))
    assert not ok                                                          # 9 -> 5 is more than half left
    ok, msg = fp.s5(_csv(tmp_path, ["2026-10-03,forge,pwsh,adopted,9,5", "2026-10-03,engine,git,adopted,10,5"]))
    assert ok and "engine/git 10 -> 5" in msg


def test_s5_without_the_record_is_open(tmp_path: Path) -> None:
    ok, msg = fp.s5(tmp_path / "missing.csv")
    assert not ok and "no adopted.csv" in msg


def _skill(skills: Path, name: str, trial: dict | None = None) -> None:
    d = skills / name
    (d / "references").mkdir(parents=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\n---\n", encoding="utf-8")
    if trial is not None:
        (d / "references" / "trial-proof.json").write_text(json.dumps(trial), encoding="utf-8")


def test_s6_counts_current_live_proofs_and_passing_trials(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    for i in range(5):
        _skill(skills, f"live{i}")
    _skill(skills, "trial-ok", {"runs": 12, "with_rate": 0.9, "lift": 0.4})
    _skill(skills, "trial-weak", {"runs": 12, "with_rate": 0.9, "lift": 0.1})
    _skill(skills, "trial-few", {"runs": 6, "with_rate": 1.0, "lift": 0.9})
    ok, msg = fp.s6(skills, live_ok=lambda n: n.startswith("live"))
    assert not ok and msg.startswith("6 of 8 skills proven") and "trial-ok" in msg and "trial-weak" not in msg
    _skill(skills, "live-extra")
    _skill(skills, "trial-two", {"runs": 10, "with_rate": 0.8, "lift": 0.3})
    ok, msg = fp.s6(skills, live_ok=lambda n: n.startswith("live"))
    assert ok and msg.startswith("8 of 10 skills proven")


def test_s6_on_the_real_skills_names_the_four_fleet_skills() -> None:
    ok, msg = fp.s6()
    assert "pwsh-for-bash-writers" in msg and "real-browser-automation" in msg


def _pack(skills: Path, name: str, listing: str, rate: float | None) -> None:
    d = skills / name
    d.mkdir(parents=True)
    (d / "listing.md").write_text(listing, encoding="utf-8")
    if rate is not None:
        (d / "eval_report.json").write_text(json.dumps({"rate": rate}), encoding="utf-8")


def test_s3_needs_a_live_url_and_a_tested_pack(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    _pack(skills, "draft-pack", "# Listing\nstatus: PREP-ONLY\n", 0.9)
    ok, msg = fp.s3(skills)
    assert not ok and "no listing.md" in msg
    _pack(skills, "untested-pack", "Live listing: https://shop.example/untested\n", None)
    ok, msg = fp.s3(skills)
    assert not ok and "below" in msg
    _pack(skills, "good-pack", "# Listing\nLive listing: https://shop.example/good\n", 0.833)
    ok, msg = fp.s3(skills)
    assert ok and "good-pack" in msg  # an untested live listing earlier in name order does not hide a good one


def test_s3_met(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    _pack(skills, "good-pack", "# Listing\nLive listing: https://shop.example/good\n", 0.833)
    ok, msg = fp.s3(skills)
    assert ok and "good-pack" in msg and "https://shop.example/good" in msg


def test_s3_a_pack_folder_counts_only_when_pack_check_passes(tmp_path: Path, monkeypatch) -> None:
    skills, packs = tmp_path / "skills", tmp_path / "packs"
    skills.mkdir()
    _pack(packs, "fleet-vol-1", "# Fleet\nLive listing: https://shop.example/fleet\n", None)
    monkeypatch.setattr(fp, "PACK_CHECK", tmp_path / "pack_check.py")
    ok, msg = fp.s3(skills, packs)
    assert not ok and "has not landed" in msg
    (tmp_path / "pack_check.py").write_text("print('RESULT FAIL 2 findings')\nraise SystemExit(1)\n", encoding="utf-8")
    ok, msg = fp.s3(skills, packs)
    assert not ok and "not tested" in msg and "RESULT FAIL" in msg
    (tmp_path / "pack_check.py").write_text("print('RESULT PASS')\n", encoding="utf-8")
    ok, msg = fp.s3(skills, packs)
    assert ok and "fleet-vol-1" in msg and "https://shop.example/fleet" in msg


def test_s1_met_cache_answers_with_no_scan(tmp_path: Path, monkeypatch) -> None:
    """S1 record-first: a fresh cache that already proves the bar is met with no database scan."""
    import adopted_after as aa  # noqa: E402
    monkeypatch.setattr(aa, "cached_skill_loads", lambda *a, **k: ({"forge": 8, "center": 4}, True))
    monkeypatch.setattr(fp, "skill_loads",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("met cache must not scan")))
    ok, msg = fp.s1()
    assert ok and "12 loads" in msg and "no re-scan" in msg


def test_s1_open_cache_answers_from_cached_meter_reads(tmp_path: Path, monkeypatch) -> None:
    """S1 open but fresh cache: no re-scan, the cached meter reads answer."""
    import adopted_after as aa  # noqa: E402
    monkeypatch.setattr(aa, "cached_skill_loads", lambda *a, **k: ({"forge": 2}, True))
    monkeypatch.setattr(fp, "skill_loads",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("fresh cache must not scan")))
    ok, msg = fp.s1()
    assert not ok and "2 loads" in msg and "cached meter reads" in msg


def test_s1_explicit_path_scans_as_is_despite_a_met_cache(tmp_path: Path, monkeypatch) -> None:
    """A file given by a test (like on the command line) is read as it is, never from the cache."""
    import adopted_after as aa  # noqa: E402
    skills, own, db = _world(tmp_path)
    monkeypatch.setattr(fp, "SKILLS", skills)
    monkeypatch.setattr(fp, "ROOT", own)
    monkeypatch.setattr(aa, "cached_skill_loads",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("an explicit path never reads the cache")))
    ok, msg = fp.s1(db)
    assert not ok and "0 loads" in msg


def test_s2_met_cache_answers_with_no_scan(tmp_path: Path, monkeypatch) -> None:
    """S2 shares the breadth path: a fresh met cache answers with no database scan."""
    import adopted_after as aa  # noqa: E402
    monkeypatch.setattr(aa, "cached_skill_loads",
                        lambda *a, **k: ({"a": 1, "b": 1, "c": 1, "d": 1, "e": 1}, True))
    monkeypatch.setattr(fp, "skill_loads",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("met cache must not scan")))
    ok, msg = fp.s2()
    assert ok and "5 other repos" in msg and "no re-scan" in msg


def test_command_line_exit_codes(tmp_path: Path) -> None:
    run = lambda *a: subprocess.run([sys.executable, str(ROOT / "tools" / "finish_proof.py"), *a], capture_output=True, text=True)  # noqa: E731
    assert run("nope").returncode == 2
    assert run("s1", str(tmp_path / "missing.db")).returncode == 1
    assert run("s2", str(tmp_path / "missing.db")).returncode == 1
    assert run("s3", str(tmp_path)).returncode == 1
    assert run("s5", str(tmp_path / "missing.csv")).returncode == 1
