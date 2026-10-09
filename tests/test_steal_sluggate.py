"""Steal sluggate: same slug+semver re-export refused before any write; new version passes."""
import json
from pathlib import Path
import pytest
from book2skill import export as export_mod
REPORT = {"rate": 1.0, "total": 1, "passed": 1}
def _skill(root: Path, name="demo-skill", version="0.1.0"):
    skill = root / name
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(f"---\nname: {name}\ndescription: demo\nversion: {version}\n---\nbody\n", encoding="utf-8")
    return skill
def test_same_version_reexport_refused(tmp_path: Path):
    skill = _skill(tmp_path / "src")
    out = tmp_path / "dist"
    export_mod.export(skill, "claude", out, eval_report=REPORT)
    lock_before = json.loads((out / "claude" / skill.name / ".lock.json").read_text(encoding="utf-8"))
    assert lock_before["version"] == "0.1.0"
    zip_before = (out / "claude" / f"{skill.name}.zip").read_bytes()
    with pytest.raises(SystemExit) as exc:
        export_mod.export(skill, "claude", out, eval_report=REPORT)
    assert exc.value.code == 2
    assert "already exists" in str(exc.value) and "0.1.0" in str(exc.value)
    assert "export refused: Version 0.1.0" in str(exc.value)
    lock_after = json.loads((out / "claude" / skill.name / ".lock.json").read_text(encoding="utf-8"))
    assert lock_after["version"] == "0.1.0"
    assert (out / "claude" / f"{skill.name}.zip").read_bytes() == zip_before
def test_new_version_passes_gate(tmp_path: Path):
    skill = _skill(tmp_path / "src")
    out = tmp_path / "dist"
    export_mod.export(skill, "claude", out, eval_report=REPORT)
    (skill / "SKILL.md").write_text("---\nname: demo-skill\ndescription: demo\nversion: 0.2.0\n---\nbody\n", encoding="utf-8")
    receipt = export_mod.export(skill, "claude", out, eval_report=REPORT)
    lock = json.loads((out / "claude" / skill.name / ".lock.json").read_text(encoding="utf-8"))
    assert lock["version"] == "0.2.0"
    assert Path(receipt["dest"]).exists()
