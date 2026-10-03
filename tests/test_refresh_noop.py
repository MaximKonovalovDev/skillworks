"""K-20 [S02-C4]: single-flight refresh no-ops when chunk fingerprint matches."""
import json
import tempfile
from pathlib import Path

from book2skill import refresh as refresh_mod


def test_twice_run_refresh_second_noops_with_receipt(tmp_path: Path) -> None:
    # Fixture lives under %TEMP% (pytest tmp_path is rooted at %TEMP% on win32).
    assert str(tmp_path).startswith(tempfile.gettempdir())
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about leases", encoding="utf-8")
    (work / "chunks" / "0001.txt").write_text("chapter about requeue", encoding="utf-8")

    first = refresh_mod.refresh(work)
    assert first["changed"] is True
    assert first["stage"] == "refresh"
    assert (work / "index.jsonl").exists()
    index_before = (work / "index.jsonl").read_text(encoding="utf-8")

    second = refresh_mod.refresh(work)
    assert second["changed"] is False
    assert second["stage"] == "refresh"
    assert second["fingerprint"] == refresh_mod.fingerprint(work)
    assert second["fingerprint"] == first["fingerprint"]
    # single-flight: index untouched on no-op
    assert (work / "index.jsonl").read_text(encoding="utf-8") == index_before
    # receipt persisted for the no-op run
    receipt = json.loads((work / "receipt.json").read_text(encoding="utf-8"))
    assert receipt == second
    assert receipt["changed"] is False
