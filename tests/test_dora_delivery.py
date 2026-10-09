"""dora-delivery: every claim of SKILL.md run against the real script.

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
SKILL = ROOT / "skills" / "dora-delivery"
SCRIPT = SKILL / "scripts" / "dora_delivery.py"
pytestmark = pytest.mark.skipif(not SCRIPT.is_file(), reason="skill not built yet")

# Lines SKILL.md must carry exactly as the script prints them. Success line GRADE <overall> deploy <d> lead <l> fail <f> restore <r>, plus ERROR with exit 2.
NEEDLES = ("GRADE", "deploy", "lead", "fail", "restore", "ERROR", "exit 2")


def run_tool(*args: str):
    """The script as a subprocess, stdin closed. Use it in the tests of the real work below."""
    return stock.run_script(SCRIPT, *args)


def write_input(tmp_path: Path, data: dict) -> Path:
    src = tmp_path / "metrics.json"
    src.write_text(json.dumps(data), encoding="utf-8")
    return src


def test_help_runs_without_a_prompt() -> None:
    stock.help_runs(SCRIPT, "--input", "--out")


def test_skill_md_documents_what_the_script_prints() -> None:
    stock.skill_md_documents(SKILL, NEEDLES)


@live
def test_an_installed_copy_runs_from_another_folder_through_pwsh(tmp_path: Path) -> None:
    """Install the skill like another repo does, then run it from pwsh from another folder."""
    copy = stock.installed_copy(tmp_path, "dora-delivery", "scripts/dora_delivery.py", skills=SKILL.parent)
    code, said = copy.run("--help")
    assert code == 0 and "--input" in said
    copy.assert_nothing_written_elsewhere()


def test_elite_input_grades_elite(tmp_path: Path) -> None:
    src = write_input(tmp_path, {"deploy_per_week": 14, "lead_hours": 2, "fail_pct": 5, "restore_hours": 3})
    out = tmp_path / "grade.json"
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip() == "GRADE elite deploy elite lead elite fail elite restore elite"
    rec = json.loads(out.read_text(encoding="utf-8"))
    assert rec["overall"] == "elite" and rec["tool"] == "dora-delivery"


def test_mixed_input_overall_is_weakest_link(tmp_path: Path) -> None:
    src = write_input(tmp_path, {"deploy_per_week": 14, "lead_hours": 2, "fail_pct": 50, "restore_hours": 3})
    out = tmp_path / "grade.json"
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip() == "GRADE low deploy elite lead elite fail low restore elite"
    rec = json.loads(out.read_text(encoding="utf-8"))
    assert rec["overall"] == "low" and rec["fail"] == "low"


def test_high_input_grades_high(tmp_path: Path) -> None:
    src = write_input(tmp_path, {"deploy_per_week": 2, "lead_hours": 100, "fail_pct": 20, "restore_hours": 100})
    out = tmp_path / "grade.json"
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip() == "GRADE high deploy high lead high fail high restore high"


def test_missing_key_is_refused_with_nothing_written(tmp_path: Path) -> None:
    src = write_input(tmp_path, {"deploy_per_week": 2, "lead_hours": 100, "fail_pct": 20})
    out = tmp_path / "grade.json"
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 2 and r.stdout.startswith("ERROR") and "restore_hours" in r.stdout, r.stdout + r.stderr
    assert "Traceback" not in r.stderr
    assert not out.exists()


def test_out_of_range_value_is_refused_with_nothing_written(tmp_path: Path) -> None:
    src = write_input(tmp_path, {"deploy_per_week": 2, "lead_hours": 100, "fail_pct": 120, "restore_hours": 5})
    out = tmp_path / "grade.json"
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 2 and r.stdout.startswith("ERROR") and "fail_pct" in r.stdout, r.stdout + r.stderr
    assert not out.exists()


def test_missing_file_is_refused_with_nothing_written(tmp_path: Path) -> None:
    out = tmp_path / "grade.json"
    r = run_tool("--input", str(tmp_path / "nope.json"), "--out", str(out))
    assert r.returncode == 2 and r.stdout.startswith("ERROR"), r.stdout + r.stderr
    assert not out.exists()
