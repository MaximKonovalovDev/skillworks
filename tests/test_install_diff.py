"""J4: installer --check names each missing/changed/extra file (chezmoi verify/diff idea)."""
import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("install_fleet_skills", ROOT / "tools" / "install_fleet_skills.py")
inst = importlib.util.module_from_spec(spec)
sys.modules["install_fleet_skills"] = inst
spec.loader.exec_module(inst)
BUILT = [n for n in inst.FLEET if (inst.SKILLS / n / "SKILL.md").is_file()]
@pytest.mark.skipif(not BUILT, reason="no fleet skill built yet")
def test_stale_names_missing_changed_extra(tmp_path: Path) -> None:
    name = BUILT[0]
    missing = inst.stale(name, tmp_path)
    assert any(m == "missing SKILL.md" for m in missing)
    assert inst.main(["--to", str(tmp_path), name]) == 0
    assert inst.stale(name, tmp_path) == []
    (tmp_path / name / "SKILL.md").write_text("drifted", encoding="utf-8")
    (tmp_path / name / "extra-note.md").write_text("x", encoding="utf-8")
    problems = inst.stale(name, tmp_path)
    assert "changed SKILL.md" in problems
    assert "extra extra-note.md" in problems
@pytest.mark.skipif(not BUILT, reason="no fleet skill built yet")
def test_check_output_names_each_file(tmp_path: Path) -> None:
    name = BUILT[0]
    assert inst.main(["--to", str(tmp_path), name]) == 0
    (tmp_path / name / "SKILL.md").write_text("drifted", encoding="utf-8")
    (tmp_path / name / "extra-note.md").write_text("x", encoding="utf-8")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = inst.main(["--to", str(tmp_path), "--check", name])
    out = buf.getvalue()
    assert rc == 1
    assert "STALE" in out and name in out
    assert "changed SKILL.md" in out
    assert "extra extra-note.md" in out
    assert inst.main(["--to", str(tmp_path), name]) == 0
    buf2 = io.StringIO()
    with redirect_stdout(buf2):
        rc2 = inst.main(["--to", str(tmp_path), "--check", name])
    assert rc2 == 0
    assert "copy matches the source" in buf2.getvalue()
@pytest.mark.skipif(not BUILT, reason="no fleet skill built yet")
def test_manifest_refuses_extra(tmp_path: Path) -> None:
    """STEAL S lockfile-lint idea: installed set validated against manifest, extras fail."""
    name = BUILT[0]
    assert inst.main(["--to", str(tmp_path), name]) == 0
    (tmp_path / name / "planted-extra.md").write_text("x", encoding="utf-8")
    assert "planted-extra.md" in inst.outside_manifest(name, tmp_path)
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = inst.main(["--to", str(tmp_path), "--check", name])
    assert rc == 1
    assert "extra planted-extra.md" in buf.getvalue()
