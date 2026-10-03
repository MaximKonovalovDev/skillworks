"""tools/install_fleet_skills.py: a copy matches the source, drift is seen, dev-only files stay home."""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("install_fleet_skills", ROOT / "tools" / "install_fleet_skills.py")
inst = importlib.util.module_from_spec(spec)
sys.modules["install_fleet_skills"] = inst
spec.loader.exec_module(inst)

BUILT = [n for n in inst.FLEET if (inst.SKILLS / n / "SKILL.md").is_file()]


@pytest.mark.skipif(not BUILT, reason="no fleet skill built yet")
def test_install_then_check_then_drift(tmp_path: Path) -> None:
    name = BUILT[0]
    assert inst.main(["--to", str(tmp_path), name]) == 0
    assert (tmp_path / name / "SKILL.md").read_bytes() == (inst.SKILLS / name / "SKILL.md").read_bytes()
    assert inst.main(["--to", str(tmp_path), "--check", name]) == 0
    (tmp_path / name / "SKILL.md").write_text("edited", encoding="utf-8")
    assert inst.main(["--to", str(tmp_path), "--check", name]) == 1
    (tmp_path / name / "extra.md").write_text("x", encoding="utf-8")
    assert "extra extra.md" in inst.stale(name, tmp_path)
    assert inst.main(["--to", str(tmp_path), name]) == 0  # copy repairs it and removes the extra file
    assert inst.main(["--to", str(tmp_path), "--check", name]) == 0
    assert not (tmp_path / name / "extra.md").exists()


def test_dev_only_files_are_not_copied() -> None:
    if not (inst.SKILLS / "pwsh-for-bash-writers" / "SKILL.md").is_file():
        pytest.skip("pwsh-for-bash-writers not built")
    names = {p.name for p in inst.payload("pwsh-for-bash-writers")}
    assert "SKILL.md" in names and "pairs.md" in names and "errors.md" in names
    assert not names & inst.SKIP_FILES


def test_unknown_skill_is_refused(tmp_path: Path) -> None:
    assert inst.main(["--to", str(tmp_path), "no-such-skill"]) == 2
