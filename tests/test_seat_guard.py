"""Seat guard: fails on untracked files under skills/, passes on a clean tree."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "seat_guard.py"


def run(*args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(TOOL), *args], cwd=ROOT,
                       capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr)


def make_repo(base: Path, skills_files: list[str] = (), other_files: list[str] = ()) -> Path:
    (base / "skills").mkdir(parents=True, exist_ok=True)
    for rel in skills_files:
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("new\n", encoding="utf-8")
    for rel in other_files:
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("new\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=base, check=True, timeout=60)
    return base


def test_clean_tree_passes(tmp_path: Path) -> None:
    root = make_repo(tmp_path / "clean")
    code, out = run("--root", str(root))
    assert code == 0, out
    assert "RESULT PASS" in out


def test_untracked_file_under_skills_fails(tmp_path: Path) -> None:
    root = make_repo(tmp_path / "dirty", ["skills/new-skill/SKILL.md"])
    code, out = run("--root", str(root))
    assert code == 1, out
    assert "RESULT FAIL" in out
    assert "skills/new-skill/SKILL.md" in out


def test_untracked_file_outside_skills_passes(tmp_path: Path) -> None:
    root = make_repo(tmp_path / "outside", [], ["tools/scratch.py"])
    code, out = run("--root", str(root))
    assert code == 0, out
    assert "RESULT PASS" in out


def test_real_skills_tree_has_no_untracked_files() -> None:
    code, out = run()
    assert code == 0, out
    assert "RESULT PASS" in out


def test_help_exits_zero() -> None:
    assert run("--help")[0] == 0
