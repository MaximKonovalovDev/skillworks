"""refactoring-to-rust: every claim of SKILL.md run against the real script.

The script is started as a real subprocess with stdin closed (headless: no prompts). The three stock tests (--help runs,
SKILL.md documents what the script prints, an installed copy runs through pwsh) are written once in tests/skill_stock.py;
this file calls them and holds the tests of the real work.
"""
from pathlib import Path

import pytest

import skill_stock as stock
from skill_stock import live

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "refactoring-to-rust"
SCRIPT = SKILL / "scripts" / "refactoring_to_rust.py"
pytestmark = pytest.mark.skipif(not SCRIPT.is_file(), reason="skill not built yet")

# Lines SKILL.md must carry exactly as the script prints them.
NEEDLES = ("PORTED", "ERROR", "exit 2")


def run_tool(*args: str):
    """The script as a subprocess, stdin closed. Use it in the tests of the real work below."""
    return stock.run_script(SCRIPT, *args)


def test_help_runs_without_a_prompt() -> None:
    stock.help_runs(SCRIPT, "--input", "--out")


def test_skill_md_documents_what_the_script_prints() -> None:
    stock.skill_md_documents(SKILL, NEEDLES)


@live
def test_an_installed_copy_runs_from_another_folder_through_pwsh(tmp_path: Path) -> None:
    """Install the skill like another repo does, then run it from pwsh from another folder."""
    copy = stock.installed_copy(tmp_path, "refactoring-to-rust", "scripts/refactoring_to_rust.py", skills=SKILL.parent)
    code, said = copy.run("--help")
    assert code == 0 and "--input" in said
    copy.assert_nothing_written_elsewhere()


SAMPLE = "\n".join(
    [
        "C: char* name = get_name();",
        "C: extern int solve(const uint8_t* board);",
        "PYTHON: class Fighter: pass",
        "PYTHON: raise ValueError(hp)",
        "JS: const level = await fetchLevel(url);",
        "JS: const data = JSON.parse(text);",
        "UNKNOWN: hello world",
    ]
)


def test_ported_counts_patterns_and_writes_the_report(tmp_path: Path) -> None:
    src = tmp_path / "in.txt"
    out = tmp_path / "report.txt"
    src.write_text(SAMPLE, encoding="utf-8")
    result = run_tool("--input", str(src), "--out", str(out))
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("PORTED ")
    assert "7 snippets" in result.stdout
    body = out.read_text(encoding="utf-8")
    for tag in ("C-STRING", "FFI-BOUNDARY", "PYCLASS-STRUCT", "RESULT-ERROR", "WASM-ASYNC", "SERDE-JSON", "OTHER"):
        assert tag in body


def test_missing_input_writes_nothing(tmp_path: Path) -> None:
    out = tmp_path / "report.txt"
    result = run_tool("--input", str(tmp_path / "nope.txt"), "--out", str(out))
    assert result.returncode == 2
    assert "ERROR missing input" in result.stdout
    assert not out.exists()


def test_empty_input_writes_nothing(tmp_path: Path) -> None:
    src = tmp_path / "in.txt"
    out = tmp_path / "report.txt"
    src.write_text("\n   \n", encoding="utf-8")
    result = run_tool("--input", str(src), "--out", str(out))
    assert result.returncode == 2
    assert "ERROR empty input" in result.stdout
    assert not out.exists()


def test_unknown_lines_map_to_other(tmp_path: Path) -> None:
    src = tmp_path / "in.txt"
    out = tmp_path / "report.txt"
    src.write_text("UNKNOWN: hello world\n", encoding="utf-8")
    result = run_tool("--input", str(src), "--out", str(out))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 patterns from 1 snippets" in result.stdout
    assert "OTHER" in out.read_text(encoding="utf-8")

