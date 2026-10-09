# find_price_markers fails loudly on unreadable or corrupt carriers.
# Good fixtures keep prior output. Corrupt fixtures raise naming the file.
from pathlib import Path
import pytest
from book2skill import build as build_mod
def _skill(tmp_path, name="s"):
    d = tmp_path / name
    d.mkdir(parents=True, exist_ok=True)
    return d
def test_good_markers_unchanged(tmp_path):
    s = _skill(tmp_path, "good")
    (s / "price.txt").write_text("$10\n", encoding="utf-8")
    (s / "pack.json").write_text("{\"price_usd\": 25}", encoding="utf-8")
    (s / "listing.md").write_text("- Price $15\n", encoding="utf-8")
    marks = build_mod.find_price_markers(s)
    assert "price.txt names a price" in marks
    assert "pack.json price_usd 25" in marks
    assert any(m.startswith("listing.md prices it") for m in marks)
    assert len(marks) == 3
def test_empty_returns_no_markers(tmp_path):
    s = _skill(tmp_path, "empty")
    assert build_mod.find_price_markers(s) == []
def test_corrupt_pack_json_raises(tmp_path):
    s = _skill(tmp_path, "badpack")
    (s / "pack.json").write_text("{ not json", encoding="utf-8")
    with pytest.raises(ValueError, match="pack.json"):
        build_mod.find_price_markers(s)
def test_corrupt_price_txt_raises(tmp_path):
    s = _skill(tmp_path, "badprice")
    (s / "price.txt").write_bytes(b"\xff\xfe\xfd")
    with pytest.raises((OSError, ValueError), match="price.txt"):
        build_mod.find_price_markers(s)
def test_corrupt_listing_md_raises(tmp_path):
    s = _skill(tmp_path, "badlisting")
    (s / "listing.md").write_bytes(b"\xff\xfe\xfd")
    with pytest.raises((OSError, ValueError), match="listing.md"):
        build_mod.find_price_markers(s)
def test_unreadable_price_txt_raises(tmp_path, monkeypatch):
    s = _skill(tmp_path, "unreadprice")
    (s / "price.txt").write_text("$10\n", encoding="utf-8")
    orig = Path.read_text
    def bad(self, *a, **k):
        if self.name == "price.txt":
            raise OSError("disk gone")
        return orig(self, *a, **k)
    monkeypatch.setattr(Path, "read_text", bad)
    with pytest.raises(OSError, match="price.txt"):
        build_mod.find_price_markers(s)
def test_unreadable_pack_json_raises(tmp_path, monkeypatch):
    s = _skill(tmp_path, "unreadpack")
    (s / "pack.json").write_text("{\"price_usd\": 5}", encoding="utf-8")
    orig = Path.read_text
    def bad(self, *a, **k):
        if self.name == "pack.json":
            raise OSError("disk gone")
        return orig(self, *a, **k)
    monkeypatch.setattr(Path, "read_text", bad)
    with pytest.raises(OSError, match="pack.json"):
        build_mod.find_price_markers(s)
def test_unreadable_listing_md_raises(tmp_path, monkeypatch):
    s = _skill(tmp_path, "unreadlisting")
    (s / "listing.md").write_text("- Price $9\n", encoding="utf-8")
    orig = Path.read_text
    def bad(self, *a, **k):
        if self.name == "listing.md":
            raise OSError("disk gone")
        return orig(self, *a, **k)
    monkeypatch.setattr(Path, "read_text", bad)
    with pytest.raises(OSError, match="listing.md"):
        build_mod.find_price_markers(s)

