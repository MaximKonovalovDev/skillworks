"""Layer slice: second refresh on matching fingerprint is an instant no-op."""
import json
import tempfile
import time
from pathlib import Path

from book2skill import refresh as refresh_mod


def test_second_refresh_noop_is_instant(tmp_path: Path) -> None:
    assert str(tmp_path).startswith(tempfile.gettempdir())
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about leases", encoding="utf-8")
    (work / "chunks" / "0001.txt").write_text("chapter about requeue", encoding="utf-8")

    first = refresh_mod.refresh(work)
    assert first["changed"] is True
    index_before = (work / "index.jsonl").read_text(encoding="utf-8")
    mtime_before = (work / "index.jsonl").stat().st_mtime_ns

    t0 = time.perf_counter()
    second = refresh_mod.refresh(work)
    dt = time.perf_counter() - t0

    assert second["changed"] is False
    assert second["stage"] == "refresh"
    assert second["fingerprint"] == first["fingerprint"]
    assert second["fingerprint"] == refresh_mod.fingerprint(work)
    assert (work / "index.jsonl").read_text(encoding="utf-8") == index_before
    assert (work / "index.jsonl").stat().st_mtime_ns == mtime_before
    receipt = json.loads((work / "receipt.json").read_text(encoding="utf-8"))
    assert receipt == second
    assert dt < 0.5, f"second refresh took {dt:.4f}s, expected instant no-op"
    print(f"second-refresh {dt:.4f}s")
