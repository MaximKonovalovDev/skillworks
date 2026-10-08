"""Safe-archive guard for pack ZIPs (zip_problems): traversal, symlink, junk, good zip."""
import io
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pack_check as pc


def make_zip(files: dict[str, bytes], symlinks: set[str] | None = None) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, data in files.items():
            if symlinks and name in symlinks:
                info = zipfile.ZipInfo(name)
                info.external_attr = (0o120777 << 16)
                z.writestr(info, data)
            else:
                z.writestr(name, data)
    return buf.getvalue()


def test_traversal_entry_refused():
    payload = make_zip({"skills/alpha/SKILL.md": b"ok", "../escape.txt": b"x"})
    problems, _ = pc.zip_problems(payload)
    assert any("unsafe paths" in p and "escape" in p for p in problems)


def test_absolute_entry_refused():
    payload = make_zip({"skills/alpha/SKILL.md": b"ok", "/abs.txt": b"x"})
    problems, _ = pc.zip_problems(payload)
    assert any("unsafe paths" in p for p in problems)


def test_symlink_refused():
    payload = make_zip(
        {"skills/alpha/SKILL.md": b"ok", "skills/alpha/link.md": b"target"},
        symlinks={"skills/alpha/link.md"},
    )
    problems, _ = pc.zip_problems(payload)
    assert any("symlink" in p for p in problems)


def test_junk_extension_refused():
    payload = make_zip({"skills/alpha/SKILL.md": b"ok", "skills/alpha/draft.swp": b"x"})
    problems, _ = pc.zip_problems(payload)
    assert any("junk files" in p for p in problems)


def test_good_zip_still_passes():
    payload = make_zip({"skills/alpha/SKILL.md": b"ok", "manifest.json": b"{}"})
    problems, members = pc.zip_problems(payload)
    assert problems == []
    assert set(members) == {"skills/alpha/SKILL.md", "manifest.json"}
