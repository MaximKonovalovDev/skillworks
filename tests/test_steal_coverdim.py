"""Store cover dimensions: PNG and GIF headers read stdlib-only, missing file fails clean."""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pack_build as pb

PNG_W, PNG_H = 320, 200
GIF_W, GIF_H = 16, 12


def make_png(path, w, h):
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_data + struct.pack(">I", 0)
    iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", 0)
    path.write_bytes(sig + ihdr + iend)


def make_gif(path, w, h):
    path.write_bytes(b"GIF89a" + struct.pack("<HH", w, h) + b"\x00\x00\x00")


def test_png_dimensions(tmp_path):
    p = tmp_path / "cover.png"
    make_png(p, PNG_W, PNG_H)
    assert pb.cover_dimensions(p) == (PNG_W, PNG_H)
    print(f"PNG header reads {PNG_W}x{PNG_H}")


def test_gif_dimensions(tmp_path):
    p = tmp_path / "cover.gif"
    make_gif(p, GIF_W, GIF_H)
    assert pb.cover_dimensions(p) == (GIF_W, GIF_H)
    print(f"GIF header reads {GIF_W}x{GIF_H}")


def test_missing_file_errors_cleanly(tmp_path):
    try:
        pb.cover_dimensions(tmp_path / "nope.png")
    except FileNotFoundError as err:
        assert "nope.png" in str(err)
    else:
        raise AssertionError("missing cover did not raise FileNotFoundError")


def test_undersized_cover_warns(tmp_path):
    small = tmp_path / "small.png"
    make_png(small, PNG_W, PNG_H)
    warn = pb.cover_warning(small)
    assert warn is not None and f"{PNG_W}x{PNG_H}" in warn
    big = tmp_path / "big.png"
    make_png(big, 1280, 720)
    assert pb.cover_warning(big) is None
