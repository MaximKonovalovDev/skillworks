"""K-41 [STEAL-ZIP]: export also writes out/<target>/<name>.zip (SKILL.md at root).

Dotfiles skipped, gate untouched, no nesting when --out sits inside the skill dir.
"""
import json
import zipfile
from pathlib import Path

import pytest

from book2skill import export as export_mod

REPORT = {"rate": 1.0, "total": 1, "passed": 1}
LOW_REPORT = {"rate": 0.5, "total": 2, "passed": 1}


def _skill(root: Path, name: str = "demo-skill") -> Path:
    skill = root / name
    (skill / "references").mkdir(parents=True)
    (skill / "scripts").mkdir(parents=True)
    (skill / "assets").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: demo skill for zip\n---\nbody\n", encoding="utf-8")
    (skill / "references" / "a.md").write_text("reference a\n", encoding="utf-8")
    (skill / "scripts" / "run.py").write_text("print('hi')\n", encoding="utf-8")
    (skill / "assets" / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    return skill


def _check_zip(zip_path: Path, skill: Path) -> list[str]:
    assert zip_path.is_file(), f"missing ZIP artifact {zip_path}"
    assert zipfile.is_zipfile(zip_path), f"{zip_path} is not a valid ZIP"
    with zipfile.ZipFile(zip_path) as bundle:
        names = bundle.namelist()
        assert "SKILL.md" in names, f"SKILL.md not at ZIP root: {names[:8]}"
        assert not any(n.startswith(f"{skill.name}/") for n in names), "skill wrapped in a top folder"
        assert "references/a.md" in names
        assert "scripts/run.py" in names
        assert "assets/logo.png" in names
        assert not any(n.startswith(".") or "/." in n for n in names), "dotfiles shipped"
        assert not any("export" in n for n in names), "own output nested into the ZIP"
        # raw bytes: write_text stores CRLF on Windows, read_text would hide that
        assert bundle.read("SKILL.md") == (skill / "SKILL.md").read_bytes()
    return names


def test_claude_export_yields_importable_zip(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    dist = tmp_path / "dist"
    receipt = export_mod.export(skill, "claude", dist, eval_report=REPORT)
    assert receipt["zip"] == str(dist / "claude" / f"{skill.name}.zip")
    _check_zip(Path(receipt["zip"]), skill)


def test_zip_for_every_target(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    dist = tmp_path / "dist"
    for target in export_mod.TARGETS:
        receipt = export_mod.export(skill, target, dist, eval_report=REPORT)
        _check_zip(Path(receipt["zip"]), skill)


def test_gate_refusal_writes_no_zip(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    dist = tmp_path / "dist"
    with pytest.raises(SystemExit) as exc:
        export_mod.export(skill, "claude", dist, eval_report=LOW_REPORT)
    assert "refused" in str(exc.value)
    assert not (dist / "claude" / skill.name).exists()
    assert not (dist / "claude" / f"{skill.name}.zip").exists()


def test_out_inside_skill_never_nests_zip(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    out = skill / "export"
    for target in export_mod.TARGETS:
        export_mod.export(skill, target, out, eval_report=REPORT)
    # second round sees the first round's output (dirs and ZIPs)
    for target in export_mod.TARGETS:
        receipt = export_mod.export(skill, target, out, eval_report=REPORT)
        _check_zip(Path(receipt["zip"]), skill)
    dest = out / "claude" / skill.name
    assert not (dest / "export").exists()
    assert not (dest / f"{skill.name}.zip").exists()
    assert list(dest.rglob("*.zip")) == []


def test_progit_branching_claude_zip(tmp_path: Path) -> None:
    """The row's done-when: progit-branching claude export yields an importable ZIP."""
    skill = Path("skills/progit-branching")
    if not skill.is_dir():
        pytest.skip("progit-branching skill not present")
    report = json.loads((skill / "eval_report.json").read_text(encoding="utf-8"))
    assert report["rate"] >= export_mod.GATE
    dist = tmp_path / "dist"
    receipt = export_mod.export(skill, "claude", dist, eval_report=report)
    zip_path = Path(receipt["zip"])
    assert zipfile.is_zipfile(zip_path)
    with zipfile.ZipFile(zip_path) as bundle:
        names = bundle.namelist()
        assert "SKILL.md" in names
        assert not any(n.startswith(".") or "/." in n for n in names)
