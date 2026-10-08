"""brooks-law-team: every claim of SKILL.md run against the real script.

The script is started as a real subprocess with stdin closed (headless: no prompts). The three stock tests (--help runs,
SKILL.md documents what the script prints, an installed copy runs through pwsh) are written once in tests/skill_stock.py;
this file calls them and holds the tests of the skill own work.
"""
import json
from pathlib import Path

import pytest

import skill_stock as stock
from skill_stock import live

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "brooks-law-team"
SCRIPT = SKILL / "scripts" / "brooks_law_team.py"
pytestmark = pytest.mark.skipif(not SCRIPT.is_file(), reason="skill not built yet")

# Lines SKILL.md must carry exactly as the script prints them.
NEEDLES = ("PLAN n=", "HOLD n=", "channels=", "integrity PASS", "integrity FAIL",
           "late staff on a short clock", "team over 7 split in two",
           "design owners keep 1 or 2", "ERROR", "exit 2", "report.json", "plan.txt")


def run_tool(*args: str):
    """The script as a subprocess, stdin closed. Use it in the tests of the real work below."""
    return stock.run_script(SCRIPT, *args)


def write_plan(folder: Path, plan: dict) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    src = folder / "plan.json"
    src.write_text(json.dumps(plan), encoding="utf-8")
    return src


def test_help_runs_without_a_prompt() -> None:
    stock.help_runs(SCRIPT, "--input", "--out")


def test_skill_md_documents_what_the_script_prints() -> None:
    stock.skill_md_documents(SKILL, NEEDLES, "references/rules.md")


@live
def test_an_installed_copy_runs_from_another_folder_through_pwsh(tmp_path: Path) -> None:
    """Install the skill like another repo does, then run it from pwsh from another folder."""
    copy = stock.installed_copy(tmp_path, "brooks-law-team", "scripts/brooks_law_team.py", skills=SKILL.parent)
    code, said = copy.run("--help")
    assert code == 0 and "--input" in said
    copy.assert_nothing_written_elsewhere()


def test_channels_math_n_five_ten_n_eight_28(tmp_path: Path) -> None:
    out = tmp_path / "o"
    src = write_plan(tmp_path / "p", {"n": 5, "design_owners": 1, "weeks_left": 10})
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("PLAN n=5 channels=10 integrity PASS"), r.stdout
    assert "1 chief + 4 support" in r.stdout
    rep = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert rep["channels"] == 10 and rep["verdict"] == "PLAN"
    assert (out / "plan.txt").read_text(encoding="utf-8").count("10") >= 1


def test_grown_channels_quoted_before_deciding(tmp_path: Path) -> None:
    out = tmp_path / "o"
    plan = {"n": 5, "late_add": 3, "design_owners": 1, "weeks_left": 4, "splittable": False}
    r = run_tool("--input", str(write_plan(tmp_path / "p", plan)), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("HOLD n=5 channels=10 to 28"), r.stdout
    rep = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert rep["grown_channels"] == 28 and rep["added_channels"] == 18


def test_hold_late_staff_on_a_short_clock(tmp_path: Path) -> None:
    out = tmp_path / "o"
    plan = {"n": 4, "late_add": 2, "design_owners": 1, "weeks_left": 3, "splittable": False}
    r = run_tool("--input", str(write_plan(tmp_path / "p", plan)), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("HOLD"), r.stdout
    assert "late staff on a short clock" in r.stdout


def test_plan_late_staff_with_long_clock_or_splittable(tmp_path: Path) -> None:
    plans = ({"n": 4, "late_add": 2, "design_owners": 1, "weeks_left": 10, "splittable": False},
             {"n": 4, "late_add": 2, "design_owners": 1, "weeks_left": 3, "splittable": True})
    for i, plan in enumerate(plans):
        out = tmp_path / f"o{i}"
        r = run_tool("--input", str(write_plan(tmp_path / f"p{i}", plan)), "--out", str(out))
        assert r.returncode == 0, r.stdout + r.stderr
        assert r.stdout.startswith("PLAN"), r.stdout


def test_hold_team_over_seven_splits(tmp_path: Path) -> None:
    out = tmp_path / "o"
    src = write_plan(tmp_path / "p", {"n": 8, "design_owners": 1, "weeks_left": 10})
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("HOLD n=8 channels=28"), r.stdout
    assert "team over 7 split in two" in r.stdout
    assert "split rest into a second team" in r.stdout


def test_integrity_gate_two_pass_three_hold(tmp_path: Path) -> None:
    src2 = write_plan(tmp_path / "p2", {"n": 4, "design_owners": 2, "weeks_left": 10})
    r = run_tool("--input", str(src2), "--out", str(tmp_path / "o2"))
    assert r.returncode == 0 and "integrity PASS" in r.stdout, r.stdout
    src3 = write_plan(tmp_path / "p3", {"n": 4, "design_owners": 3, "weeks_left": 10})
    r = run_tool("--input", str(src3), "--out", str(tmp_path / "o3"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "integrity FAIL" in r.stdout and r.stdout.startswith("HOLD"), r.stdout
    assert "3 design owners keep 1 or 2" in r.stdout


def test_single_person_zero_channels(tmp_path: Path) -> None:
    out = tmp_path / "o"
    src = write_plan(tmp_path / "p", {"n": 1, "design_owners": 1, "weeks_left": 10})
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 0 and "channels=0" in r.stdout, r.stdout
    assert r.stdout.startswith("PLAN"), r.stdout


@pytest.mark.parametrize("case,plan", [
    ("bad-n", {"n": 0, "design_owners": 1, "weeks_left": 10}),
    ("bad-owners", {"n": 4, "design_owners": 0, "weeks_left": 10}),
    ("bad-weeks", {"n": 4, "design_owners": 1, "weeks_left": -1}),
    ("bad-late", {"n": 4, "late_add": -1, "design_owners": 1, "weeks_left": 10}),
    ("bad-split", {"n": 4, "design_owners": 1, "weeks_left": 10, "splittable": "yes"}),
    ("missing-key", {"n": 4, "weeks_left": 10}),
    ("unknown-key", {"n": 4, "design_owners": 1, "weeks_left": 10, "boss": 1}),
])
def test_bad_plan_is_an_error_with_exit_two_and_nothing_written(tmp_path: Path, case: str, plan: dict) -> None:
    src = write_plan(tmp_path / ("p-" + case), plan)
    out = tmp_path / ("o-" + case)
    before = sorted((p.name, p.read_bytes()) for p in tmp_path.rglob("*") if p.is_file())
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 2 and r.stdout.startswith("ERROR"), r.stdout + r.stderr
    assert not out.exists()
    assert before == sorted((p.name, p.read_bytes()) for p in tmp_path.rglob("*") if p.is_file())


def test_missing_file_and_bad_json_write_nothing(tmp_path: Path) -> None:
    out = tmp_path / "o"
    r = run_tool("--input", str(tmp_path / "missing.json"), "--out", str(out))
    assert r.returncode == 2 and r.stdout.startswith("ERROR") and not out.exists()
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    r = run_tool("--input", str(bad), "--out", str(tmp_path / "o2"))
    assert r.returncode == 2 and r.stdout.startswith("ERROR") and not (tmp_path / "o2").exists()


def test_out_as_file_or_as_input_is_refused(tmp_path: Path) -> None:
    src = write_plan(tmp_path / "p", {"n": 4, "design_owners": 1, "weeks_left": 10})
    filing = tmp_path / "afile"
    filing.write_text("keep me", encoding="utf-8")
    r = run_tool("--input", str(src), "--out", str(filing))
    assert r.returncode == 2 and r.stdout.startswith("ERROR refused"), r.stdout
    r = run_tool("--input", str(src), "--out", str(src))
    assert r.returncode == 2 and r.stdout.startswith("ERROR refused"), r.stdout


def test_second_run_overwrites_report(tmp_path: Path) -> None:
    out = tmp_path / "o"
    src = write_plan(tmp_path / "p", {"n": 4, "design_owners": 1, "weeks_left": 10})
    assert run_tool("--input", str(src), "--out", str(out)).returncode == 0
    src.write_text(json.dumps({"n": 5, "design_owners": 1, "weeks_left": 10}), encoding="utf-8")
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 0 and "channels=10" in r.stdout, r.stdout
    assert json.loads((out / "report.json").read_text(encoding="utf-8"))["channels"] == 10
