"""DR-1005-7 RED baseline plus trials registry: numbered runs, change log, query."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools import red_baseline_registry as red

ROOT = Path(__file__).resolve().parent.parent


def test_green_without_a_red_baseline_is_refused(tmp_path: Path) -> None:
    reg = tmp_path / "red.jsonl"
    with pytest.raises(ValueError, match="no red baseline"):
        red.record(reg, "forge", "pwsh-for-bash-writers", "green", 4)
    assert not reg.exists()


def test_red_then_green_records_numbered_runs_with_changes(tmp_path: Path) -> None:
    reg = tmp_path / "red.jsonl"
    first = red.record(reg, "forge", "pwsh-for-bash-writers", "red", 9,
                       change="before install", at="2026-10-05T10:00Z")
    second = red.record(reg, "forge", "pwsh-for-bash-writers", "green", 4,
                        change="installed v2", at="2026-10-05T12:00Z")
    assert (first["run"], second["run"]) == ("001", "002")
    rows = [json.loads(ln) for ln in reg.read_text(encoding="utf-8").splitlines()]
    assert [r["change"] for r in rows] == ["before install", "installed v2"]
    assert red.load(reg) == rows


def test_query_prints_the_first_real_before_to_after_halving(tmp_path: Path) -> None:
    reg = tmp_path / "red.jsonl"
    red.record(reg, "forge", "pwsh-for-bash-writers", "red", 9, at="2026-10-05T10:00Z")
    red.record(reg, "forge", "pwsh-for-bash-writers", "green", 4,
               change="installed v2", at="2026-10-05T12:00Z")
    ok, msg = red.query(reg)
    assert ok and "forge/pwsh-for-bash-writers 9 -> 4 (runs 001->002)" in msg


def test_query_stays_open_without_a_halving(tmp_path: Path) -> None:
    reg = tmp_path / "red.jsonl"
    assert red.query(reg) == (False, "open: no halving yet; 0 paired run(s) in 0 runs")
    red.record(reg, "forge", "pwsh-for-bash-writers", "red", 9)
    red.record(reg, "forge", "pwsh-for-bash-writers", "green", 6)
    ok, msg = red.query(reg)
    assert not ok and "open:" in msg  # 9 -> 6 is more than half left


def test_bad_phase_and_counts_are_refused(tmp_path: Path) -> None:
    reg = tmp_path / "red.jsonl"
    with pytest.raises(ValueError, match="phase must be"):
        red.record(reg, "forge", "pwsh-for-bash-writers", "blue", 1)
    with pytest.raises(ValueError, match="count up from 0"):
        red.record(reg, "forge", "pwsh-for-bash-writers", "red", -1)


def test_trial_check_asks_for_the_red_arm_in_trial_form(tmp_path: Path) -> None:
    trials = tmp_path / "trials" / "demo"
    ok, msg = red.trial_check("demo", trials)
    assert not ok and "no red baseline" in msg
    trials.mkdir(parents=True)
    (trials / "without.jsonl").write_text('{"id": "r01", "answer": "fails"}\n', encoding="utf-8")
    ok, msg = red.trial_check("demo", trials)
    assert ok and "1 without-skill run" in msg


def test_command_line_query_exits_0_on_a_halving(tmp_path: Path) -> None:
    reg = tmp_path / "red.jsonl"
    run = lambda *a: subprocess.run(  # noqa: E731
        [sys.executable, str(ROOT / "tools" / "red_baseline_registry.py"), *a],
        capture_output=True, text=True, encoding="utf-8",
        stdin=subprocess.DEVNULL, timeout=120)
    assert run("query", "--registry", str(reg)).returncode == 1
    assert run("record", "--registry", str(reg), "--repo", "forge",
               "--skill", "pwsh-for-bash-writers", "--phase", "green",
               "--failures", "4").returncode == 1  # no red yet
    assert run("record", "--registry", str(reg), "--repo", "forge",
               "--skill", "pwsh-for-bash-writers", "--phase", "red",
               "--failures", "9", "--change", "before install").returncode == 0
    assert run("record", "--registry", str(reg), "--repo", "forge",
               "--skill", "pwsh-for-bash-writers", "--phase", "green",
               "--failures", "4", "--change", "installed v2").returncode == 0
    r = run("query", "--registry", str(reg))
    assert r.returncode == 0 and "9 -> 4 (runs 001->002)" in r.stdout
    r = run("log", "--registry", str(reg))
    assert r.returncode == 0 and "installed v2" in r.stdout
