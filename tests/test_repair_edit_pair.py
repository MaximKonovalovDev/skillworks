"""Repair 002: the edit-pair re-seal grades both sealed sheets read-only."""
import json
import subprocess
import sys
from pathlib import Path

from tools import repair_edit_pair as repair

ROOT = Path(__file__).resolve().parent.parent


def test_reseal_grades_both_sealed_sheets() -> None:
    doc, _ = repair.reseal(ROOT / "evals", ROOT / "work" / "trials")
    assert doc["repair"] == "002" and doc["ok"] is True
    er, eu = doc["skills"]["edit-reread"], doc["skills"]["edit-unique"]
    assert (er["runs"], er["with_rate"], er["without_rate"], er["lift"]) == (12, 1.0, 0.3333, 0.6667)
    assert (eu["runs"], eu["with_rate"], eu["without_rate"], eu["lift"]) == (12, 1.0, 0.0, 1.0)
    assert er["fingerprint"] == "7a647ca96199e8de2c9ab8e5b3b6f611879e505006dc8e4632a15edf491e1bf1"
    assert eu["fingerprint"] == "ac0d616d900625c51af6a3e341f2a9bf58c554dc7d17bb477e87430a0ed941df"


def test_main_writes_only_own_out_and_touches_no_skill(tmp_path: Path, capsys) -> None:
    before = {s: (ROOT / "skills" / s / "references" / "trial-proof.json").read_bytes()
              for s in ("edit-reread", "edit-unique")}
    out = tmp_path / "reseal.json"
    assert repair.main(["--out", str(out)]) == 0
    text = capsys.readouterr().out
    assert "RESULT PASS" in text and out.is_file()
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert set(doc["skills"]) == {"edit-reread", "edit-unique"} and doc["ok"] is True
    for s in ("edit-reread", "edit-unique"):
        assert (ROOT / "skills" / s / "references" / "trial-proof.json").read_bytes() == before[s]
    assert "trial-proof" not in (ROOT / "tools" / "repair_edit_pair.py").read_text(encoding="utf-8")


def test_command_line_reseal(tmp_path: Path) -> None:
    out = tmp_path / "reseal.json"
    run = subprocess.run([sys.executable, str(ROOT / "tools" / "repair_edit_pair.py"), "--out", str(out)],
                         capture_output=True, text=True)
    assert run.returncode == 0 and "RESULT PASS" in run.stdout
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["skills"]["edit-reread"]["lift"] == 0.6667
    assert doc["skills"]["edit-unique"]["lift"] == 1.0
