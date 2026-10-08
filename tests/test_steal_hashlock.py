"""Hash-lock for installed fleet skills: clean lock shows no drift, tampered payload drifts."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("install_fleet_skills", ROOT / "tools" / "install_fleet_skills.py")
inst = importlib.util.module_from_spec(spec)
sys.modules["install_fleet_skills"] = inst
spec.loader.exec_module(inst)


def test_clean_lock_has_no_drift(tmp_path: Path) -> None:
    entries = {"alpha": "hello skill", "beta": "other content"}
    lock = tmp_path / "skills-lock.json"
    inst.write_lock(lock, entries)
    assert inst.lock_drift(lock, entries) is False
    print("clean drift: 0")


def test_tampered_content_reports_drift(tmp_path: Path) -> None:
    entries = {"alpha": "hello skill"}
    lock = tmp_path / "skills-lock.json"
    inst.write_lock(lock, entries)
    assert inst.lock_drift(lock, {"alpha": "tampered content"}) is True
    assert inst.lock_drift(lock, {"alpha": "hello skill", "gamma": "new skill"}) is True
    print("drift-detected: 1")
