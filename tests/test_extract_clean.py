"""extract_clean CLI prints receipt, exit 2 when in missing."""
import json
from pathlib import Path

import pytest

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


def test_main_non_utf8_succeeds(tmp_path: Path, capsys):
    src = tmp_path / "bin.txt"
    src.write_bytes(b"\xff\xfe\xfd hello \x80\x81 binary\n")
    rc = extract_clean.main(["--in", str(src), "--out", str(tmp_path / "w")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "extracted" in out
    receipt = json.loads((tmp_path / "w" / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["chars"] > 0


def test_main_empty_input_zero_chars(tmp_path: Path, capsys):
    src = tmp_path / "empty.txt"
    src.write_text("", encoding="utf-8")
    rc = extract_clean.main(["--in", str(src), "--out", str(tmp_path / "w")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "extracted 0 chars" in out
    receipt = json.loads((tmp_path / "w" / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["chars"] == 0


def test_main_engine_fallback_auto(tmp_path: Path, monkeypatch, capsys):
    src = tmp_path / "fake.pdf"
    src.write_bytes(b"%PDF-1.4 fake")
    def _boom(path):
        raise RuntimeError("markitdown down")
    def _classic(path):
        return ("fallback text", 1)
    monkeypatch.setattr(extract_mod, "_read_pdf_markitdown", _boom)
    monkeypatch.setattr(extract_mod, "_read_pdf_classic", _classic)
    rc = extract_clean.main(["--in", str(src), "--out", str(tmp_path / "w"), "--engine", "auto"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "classic-fallback" in out


def test_main_forwards_engine_auto(tmp_path: Path, monkeypatch):
    seen = {}
    def fake(src, out, include=None, engine="x"):
        seen["engine"] = engine
        return {"chars": 1, "kind": "f", "engine": engine, "md_headings": 0, "md_tables": 0, "md_fences": 0}
    monkeypatch.setattr(extract_mod, "extract", fake)
    rc = extract_clean.main(["--in", "x", "--out", str(tmp_path / "w"), "--engine", "auto"])
    assert rc == 0
    assert seen.get("engine") == "auto"


def test_main_value_error_returns_two(tmp_path: Path, monkeypatch, capsys):
    def fake(src, out, include=None, engine="x"):
        raise ValueError("bad input")
    monkeypatch.setattr(extract_mod, "extract", fake)
    rc = extract_clean.main(["--in", "x", "--out", str(tmp_path / "w")])
    assert rc == 2
    err = capsys.readouterr().err
    assert "bad input" in err


def test_main_empty_folder_returns_two(tmp_path: Path):
    empty = tmp_path / "empty_dir"
    empty.mkdir()
    rc = extract_clean.main(["--in", str(empty), "--out", str(tmp_path / "w")])
    assert rc == 2


def test_main_invalid_engine_exits_two(tmp_path: Path):
    with pytest.raises(SystemExit) as excinfo:
        extract_clean.main(["--in", "x", "--out", str(tmp_path / "w"), "--engine", "bogus"])
    assert excinfo.value.code == 2
