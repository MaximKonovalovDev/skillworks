"""extract_clean CLI prints receipt, exit 2 when in missing."""
from pathlib import Path

from book2skill import extract as extract_mod
from tools import extract_clean


def test_main_prints_receipt(monkeypatch, tmp_path: Path, capsys):
    def fake(src, out, include=None, engine="x"):
        return {"chars": 5, "kind": "f", "engine": engine, "md_headings": 1, "md_tables": 2, "md_fences": 1}
    monkeypatch.setattr(extract_mod, "extract", fake)
    rc = extract_clean.main(["--in", "x", "--out", str(tmp_path / "w")])
    assert rc == 0
    got = capsys.readouterr().out
    assert "extracted 5 chars" in got
    assert "headings 1 tables 2 fences 1" in got


def test_main_missing_returns_two(tmp_path: Path):
    rc = extract_clean.main(["--in", str(tmp_path / "no.pdf"), "--out", str(tmp_path / "w")])
    assert rc == 2
