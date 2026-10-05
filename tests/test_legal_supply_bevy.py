"""BK-1005-2: legal Bevy-plus-docs supply slice is small, sellable, mapped, ignored, sheeted."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import legal_supply_bevy as m


def test_manifest_slices_small_mapped_sellable():
    assert 4 <= len(m.SLICES) <= 6
    ids = [s["id"] for s in m.SLICES]
    assert len(set(ids)) == len(ids)
    for s in m.SLICES:
        assert s["failure_class"] in m.FAILURE_CLASSES, s
        assert 1 <= len(s["files"]) <= m.MAX_FILES_PER_SLICE, s
        assert m.is_sellable(s["license_spdx"]), s
        assert s["repo"] and s["ref"], s


def test_nc_sa_agpl_never_sold():
    for bad in ("CC-BY-NC-SA-3.0", "CC BY-NC-SA 3.0", "CC-BY-NC-4.0",
                "CC-BY-SA-4.0", "AGPL-3.0", "GPL-3.0-only", "SSPL-1.0",
                "NOASSERTION", ""):
        assert not m.is_sellable(bad), bad
    for good in ("Apache-2.0", "Apache-2.0 OR MIT", "MIT", "MIT-0", "CC-BY-4.0", "CC-BY"):
        assert m.is_sellable(good), good
    with pytest.raises(ValueError, match="never sold"):
        m.record_fetch("probe", b"x", "abc1234", "CC-BY-NC-SA-3.0")
    with pytest.raises(ValueError, match="never sold"):
        m.record_fetch("probe", b"x", "abc1234", "AGPL-3.0")


def test_sources_stay_in_ignored_work(tmp_path: Path):
    for s in m.SLICES:
        assert str(m.dest_for(s["id"])).startswith(str(ROOT / "work")), s["id"]
    with pytest.raises(ValueError, match="work/"):
        m.ensure_work_path("skills/evil/file.md")
    with pytest.raises(ValueError, match="work/"):
        m.ensure_work_path("../outside.md")
    assert "work/" in (ROOT / ".gitignore").read_text(encoding="utf-8")


def test_fetch_records_sha_and_live_licence(tmp_path: Path):
    body = b"bevy app schedule notes in our own words"
    receipt = m.record_fetch.__wrapped__ if hasattr(m.record_fetch, "__wrapped__") else None
    got = m.record_fetch("probe-slice", body, "b56fc29d3016e6", "Apache-2.0 OR MIT")
    # record_fetch writes under work/ by design; clean the probe right away.
    probe = ROOT / "work" / "legal-supply-bevy" / "probe-slice"
    try:
        assert got["sha256"] == hashlib.sha256(body).hexdigest()
        assert len(got["sha256"]) == 64
        assert got["license_spdx"] == "Apache-2.0 OR MIT"
        assert got["license_read"] == "live"
        assert got["commit"] == "b56fc29d3016e6"
        assert (probe / "receipt.json").is_file()
    finally:
        import shutil
        shutil.rmtree(probe, ignore_errors=True)
    assert receipt is None  # plain function, no hidden wrapper


def test_sheet_emits_twelve_tasks(tmp_path: Path):
    out = tmp_path / "sheet.jsonl"
    rows = m.emit_sheet(out)
    assert len(rows) == 12
    ids = [r["id"] for r in rows]
    assert len(set(ids)) == 12
    slices = {r["locator"] for r in rows}
    assert len(slices) >= 4
    for r in rows:
        assert r["kind"] in ("run", "answer"), r
        assert r["task"] and r["locator"], r
        assert isinstance(r["must"], list) and r["must"], r
    kinds = {r["kind"] for r in rows}
    assert kinds == {"run", "answer"}
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 12 and all(json.loads(l)["id"] for l in lines)


def test_cli_check_and_sheet_pass():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "legal_supply_bevy.py"), "check"],
                       capture_output=True, text=True, timeout=60, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RESULT PASS" in r.stdout
