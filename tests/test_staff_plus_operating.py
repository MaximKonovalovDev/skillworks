"""staff-plus-operating: every claim of SKILL.md run against the real script.

The script is started as a real subprocess with stdin closed (headless: no prompts). The three stock tests (--help runs,
SKILL.md documents what the script prints, an installed copy runs through pwsh) are written once in tests/skill_stock.py;
this file calls them and holds the tests of the skill real work.
"""
import json
from pathlib import Path

import pytest

import skill_stock as stock
from skill_stock import live

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "staff-plus-operating"
SCRIPT = SKILL / "scripts" / "staff_plus_operating.py"
pytestmark = pytest.mark.skipif(not SCRIPT.is_file(), reason="skill not built yet")

# Lines SKILL.md must carry exactly as the script prints them.
NEEDLES = (
    "OPERATE <archetype> checklist <p>/6 decision <title>",
    "tech-lead",
    "architect",
    "solver",
    "right-hand",
    "YYYY-MM-DD",
    "ERROR",
    "exit 2",
    "nothing written",
)


def run_tool(*args: str):
    """The script as a subprocess, stdin closed. Use it in the tests of the real work below."""
    return stock.run_script(SCRIPT, *args)


def write_brief(path: Path, **over) -> Path:
    data = {
        "title": "Migrate queue worker",
        "situation": "The queue backs up at peak and retries hide the cause.",
        "scope": "team",
        "options": ["Move to pull model", "Add partitions to push model"],
        "owner": "dana",
        "review_date": "2026-10-20",
        "risks": ["Replay on cutover"],
    }
    data.update(over)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_help_runs_without_a_prompt() -> None:
    stock.help_runs(SCRIPT, "--input", "--out")


def test_skill_md_documents_what_the_script_prints() -> None:
    stock.skill_md_documents(SKILL, NEEDLES, "references/archetypes.md", "references/operating-checklist.md", "references/decision-template.md")


@live
def test_an_installed_copy_runs_from_another_folder_through_pwsh(tmp_path: Path) -> None:
    """Install the skill like another repo does, then run it from pwsh from another folder."""
    copy = stock.installed_copy(tmp_path, "staff-plus-operating", "scripts/staff_plus_operating.py", skills=SKILL.parent)
    code, said = copy.run("--help")
    assert code == 0 and "--input" in said
    copy.assert_nothing_written_elsewhere()


@pytest.mark.parametrize("scope,archetype", [
    ("team", "tech-lead"),
    ("multi-team", "architect"),
    ("single-hard-problem", "solver"),
    ("leader-support", "right-hand"),
])
def test_scope_map_gives_the_named_archetype(tmp_path: Path, scope: str, archetype: str) -> None:
    brief = write_brief(tmp_path / "brief.json", scope=scope)
    out = tmp_path / "report.md"
    r = run_tool("--input", str(brief), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip().startswith(f"OPERATE {archetype} checklist "), r.stdout
    text = out.read_text(encoding="utf-8")
    assert f"archetype: {archetype}" in text
    assert f"scope: {scope}" in text


def test_full_brief_passes_six_of_six(tmp_path: Path) -> None:
    brief = write_brief(tmp_path / "brief.json")
    out = tmp_path / "report.md"
    r = run_tool("--input", str(brief), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip() == "OPERATE tech-lead checklist 6/6 decision Migrate queue worker"
    text = out.read_text(encoding="utf-8")
    assert text.count("PASS") >= 6
    assert "1. Move to pull model" in text
    assert "- Replay on cutover" in text
    assert "## Choice" in text
    assert "review-date: 2026-10-20" in text


def test_missing_risk_fails_only_that_line(tmp_path: Path) -> None:
    brief = write_brief(tmp_path / "brief.json", risks=[])
    out = tmp_path / "report.md"
    r = run_tool("--input", str(brief), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "checklist 5/6" in r.stdout
    text = out.read_text(encoding="utf-8")
    assert "risks-listed FAIL" in text
    assert "- none listed" in text


@pytest.mark.parametrize("case,brief_over,needle", [
    ("bad-scope", {"scope": "Team"}, "ERROR bad scope"),
    ("single-option", {"options": ["only one"]}, "ERROR bad options"),
    ("bad-date", {"review_date": "tomorrow"}, "ERROR bad review_date"),
    ("blank-owner", {"owner": "  "}, "ERROR bad owner"),
    ("long-title", {"title": "T" * 121}, "ERROR bad title"),
])
def test_bad_brief_is_refused_and_writes_nothing(tmp_path: Path, case: str, brief_over: dict, needle: str) -> None:
    brief = write_brief(tmp_path / "brief.json", **brief_over)
    out = tmp_path / "report.md"
    r = run_tool("--input", str(brief), "--out", str(out))
    assert r.returncode == 2, r.stdout + r.stderr
    assert needle in r.stdout
    assert "nothing written" in r.stdout
    assert not out.exists()


def test_out_is_input_is_refused(tmp_path: Path) -> None:
    brief = write_brief(tmp_path / "brief.json")
    before = brief.read_bytes()
    r = run_tool("--input", str(brief), "--out", str(brief))
    assert r.returncode == 2 and "refused" in r.stdout
    assert brief.read_bytes() == before


def test_missing_input_is_refused(tmp_path: Path) -> None:
    out = tmp_path / "report.md"
    r = run_tool("--input", str(tmp_path / "missing.json"), "--out", str(out))
    assert r.returncode == 2 and "ERROR input missing" in r.stdout
    assert not out.exists()


def test_bad_json_is_refused(tmp_path: Path) -> None:
    brief = tmp_path / "brief.json"
    brief.write_text("{not json", encoding="utf-8")
    out = tmp_path / "report.md"
    r = run_tool("--input", str(brief), "--out", str(out))
    assert r.returncode == 2 and "ERROR input is not JSON" in r.stdout
    assert not out.exists()


def test_report_carries_the_decision_template_fields(tmp_path: Path) -> None:
    brief = write_brief(tmp_path / "brief.json", scope="multi-team", context="Two teams share the queue.")
    out = tmp_path / "report.md"
    r = run_tool("--input", str(brief), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    text = out.read_text(encoding="utf-8")
    for field in ("# Decision:", "archetype: architect", "owner:", "review-date:", "## Situation", "## Checklist", "## Options", "## Risks", "## Choice"):
        assert field in text, field
