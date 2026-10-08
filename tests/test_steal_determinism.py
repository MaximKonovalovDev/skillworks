"""Deterministic export ZIP: same fixture exported twice hashes the same."""
import hashlib
import zipfile
from pathlib import Path

from book2skill import export as export_mod

REPORT = {"rate": 1.0, "total": 1, "passed": 1}


def _skill(root: Path, name: str = "steal-demo") -> Path:
    skill = root / name
    (skill / "references").mkdir(parents=True)
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: determinism fixture\n---\nbody\n",
        encoding="utf-8",
    )
    (skill / "references" / "a.md").write_text("reference a\n", encoding="utf-8")
    (skill / "scripts" / "run.py").write_text("print(hi)\n", encoding="utf-8")
    return skill


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_export_zip_is_byte_identical_across_reruns(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    first_out = tmp_path / "out1"
    second_out = tmp_path / "out2"
    first = export_mod.export(skill, "claude", first_out, eval_report=REPORT)
    second = export_mod.export(skill, "claude", second_out, eval_report=REPORT)
    first_zip = Path(first["zip"])
    second_zip = Path(second["zip"])
    first_hash = _sha256(first_zip)
    second_hash = _sha256(second_zip)
    print(f"first {first_hash}")
    print(f"second {second_hash}")
    assert first_hash == second_hash
    with zipfile.ZipFile(first_zip) as bundle:
        for info in bundle.infolist():
            assert info.date_time == (2020, 2, 2, 0, 0, 0), info.filename
            mode = (info.external_attr >> 16) & 0o777
            assert mode in (0o644, 0o755), (info.filename, oct(mode))

