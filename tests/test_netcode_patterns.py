"""netcode-patterns: every claim of SKILL.md run against the real script.

The script is started as a real subprocess with stdin closed (headless: no prompts). The three stock tests (--help runs,
SKILL.md documents what the script prints, an installed copy runs through pwsh) are written once in tests/skill_stock.py;
this file calls them and holds the tests of the skill's own work.
"""
import json
from pathlib import Path

import pytest

import skill_stock as stock
from skill_stock import live

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "netcode-patterns"
SCRIPT = SKILL / "scripts" / "netcode_patterns.py"
pytestmark = pytest.mark.skipif(not SCRIPT.is_file(), reason="skill not built yet")

# Lines SKILL.md must carry exactly as the script prints them.
NEEDLES = ("RUN <n> messages flags", "report.json", "ERROR", "exit 2")


def run_tool(*args: str):
    """The script as a subprocess, stdin closed. Use it in the tests of the real work below."""
    return stock.run_script(SCRIPT, *args)


def write_plan(tmp_path: Path, messages: list) -> Path:
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"messages": messages}), encoding="utf-8")
    return plan


def test_help_runs_without_a_prompt() -> None:
    stock.help_runs(SCRIPT, "--input", "--out")


def test_skill_md_documents_what_the_script_prints() -> None:
    stock.skill_md_documents(SKILL, NEEDLES)


@live
def test_an_installed_copy_runs_from_another_folder_through_pwsh(tmp_path: Path) -> None:
    """Install the skill like another repo does, then run it from pwsh from another folder."""
    copy = stock.installed_copy(tmp_path, "netcode-patterns", "scripts/netcode_patterns.py", skills=SKILL.parent)
    code, said = copy.run("--help")
    assert code == 0 and "--input" in said
    copy.assert_nothing_written_elsewhere()


def test_good_plan_runs_two_with_report(tmp_path: Path) -> None:
    plan = write_plan(tmp_path, [
        {"name": "pos", "delivery": "unreliable", "urgent": False, "size": 64, "per_second": 10},
        {"name": "score", "delivery": "reliable", "urgent": False, "size": 32, "per_second": 2},
    ])
    out = tmp_path / "out"
    r = run_tool("--input", str(plan), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip() == "RUN 2 messages flags 2 warnings 0"
    report = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert report == {"tool": "netcode-patterns", "messages": 2,
                      "flags": {"pos": "Unreliable", "score": "Reliable"}, "warnings": []}


def test_urgent_flags_map_to_no_nagle(tmp_path: Path) -> None:
    plan = write_plan(tmp_path, [
        {"name": "fast", "delivery": "unreliable", "urgent": True, "size": 64, "per_second": 10},
        {"name": "hot", "delivery": "reliable", "urgent": True, "size": 32, "per_second": 2},
    ])
    out = tmp_path / "out"
    r = run_tool("--input", str(plan), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip() == "RUN 2 messages flags 2 warnings 0"
    report = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert report["flags"] == {"fast": "UnreliableNoNagle", "hot": "ReliableNoNagle"}


def test_bad_delivery_is_refused(tmp_path: Path) -> None:
    plan = write_plan(tmp_path, [
        {"name": "pos", "delivery": "Reliable", "urgent": False, "size": 64, "per_second": 10},
    ])
    out = tmp_path / "out"
    r = run_tool("--input", str(plan), "--out", str(out))
    assert r.returncode == 2
    assert r.stdout.startswith("ERROR")
    assert not out.exists()


def test_missing_input_is_refused(tmp_path: Path) -> None:
    out = tmp_path / "out"
    r = run_tool("--input", str(tmp_path / "missing.json"), "--out", str(out))
    assert r.returncode == 2
    assert r.stdout.startswith("ERROR")
    assert not out.exists()


def test_bad_name_is_refused(tmp_path: Path) -> None:
    plan = write_plan(tmp_path, [
        {"name": "Bad-Name!", "delivery": "unreliable", "urgent": False, "size": 64, "per_second": 10},
    ])
    out = tmp_path / "out"
    r = run_tool("--input", str(plan), "--out", str(out))
    assert r.returncode == 2
    assert r.stdout.startswith("ERROR")
    assert not out.exists()


def test_warnings_count_size_and_rate(tmp_path: Path) -> None:
    plan = write_plan(tmp_path, [
        {"name": "spam", "delivery": "reliable", "urgent": False, "size": 64, "per_second": 30},
        {"name": "big", "delivery": "unreliable", "urgent": False, "size": 2000, "per_second": 5},
    ])
    out = tmp_path / "out"
    r = run_tool("--input", str(plan), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip() == "RUN 2 messages flags 2 warnings 2"
    report = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert len(report["warnings"]) == 2
