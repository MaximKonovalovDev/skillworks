"""TS-4 clean extractor: markitdown keeps structure, classic flattens it.

Fixture EPUB and PDF each hold one table and one code block. The markitdown
engine must keep both (pipe rows, fenced block, headings); the classic engine
must flatten them (counts printed, classic zeros). markitdown lives in
.tools/py (TS-4 install); the markitdown half skips when it is absent.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

from book2skill import extract as extract_mod


def _markitdown_available() -> bool:
    root = Path(__file__).resolve().parents[1] / ".tools" / "py"
    if root.is_dir() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        import markitdown  # noqa: F401
        return True
    except Exception:
        return False


def _write_epub(path: Path) -> None:
    body = (
        "<?xml version='1.0' encoding='utf-8'?>"
        "<html xmlns='http://www.w3.org/1999/xhtml'><head><title>Probe</title></head><body>"
        "<h1>Probe Chapter</h1><p>Intro line.</p>"
        "<table><tr><th>cmd</th><th>does</th></tr>"
        "<tr><td>git status</td><td>shows state</td></tr></table>"
        "<pre><code>git status --short\ngit log --oneline -3</code></pre>"
        "</body></html>"
    )
    opf = (
        "<?xml version='1.0'?><package version='3.0' xmlns='http://www.idpf.org/2007/opf' unique-identifier='b'>"
        "<metadata xmlns:dc='http://purl.org/dc/elements/1.1/'><dc:title>Probe</dc:title>"
        "<dc:identifier id='b'>probe</dc:identifier><dc:language>en</dc:language></metadata>"
        "<manifest><item id='c' href='c.xhtml' media-type='application/xhtml+xml'/></manifest>"
        "<spine><itemref idref='c'/></spine></package>"
    )
    container = (
        "<?xml version='1.0'?><container version='1.0' "
        "xmlns='urn:oasis:names:tc:opendocument:xmlns:container'><rootfiles>"
        "<rootfile full-path='OEBPS/content.opf' media-type='application/oebps-package+xml'/>"
        "</rootfiles></container>"
    )
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip")
        zf.writestr("META-INF/container.xml", container)
        zf.writestr("OEBPS/content.opf", opf)
        zf.writestr("OEBPS/c.xhtml", body)


def _esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _write_pdf(path: Path) -> None:
    """One-page PDF: bold title, ruled 2x3 table, two Courier code lines."""
    ops: list[str] = []
    ops.append("BT /F2 20 Tf 1 0 0 1 50 750 Tm (Probe Manual) Tj ET")
    ops.append("BT /F1 12 Tf 1 0 0 1 50 722 Tm (Intro line.) Tj ET")
    cells = [(55, 676, "cmd"), (205, 676, "does"),
             (55, 656, "git status"), (205, 656, "shows state"),
             (55, 636, "git log"), (205, 636, "shows history")]
    for x, y, text in cells:
        ops.append(f"BT /F1 11 Tf 1 0 0 1 {x} {y} Tm ({_esc(text)}) Tj ET")
    for y in (690, 670, 650, 630):
        ops.append(f"50 {y} m 450 {y} l S")
    for x in (50, 200, 450):
        ops.append(f"{x} 630 m {x} 690 l S")
    for y, text in ((600, "git status --short"), (585, "git log --oneline -3")):
        ops.append(f"BT /F3 11 Tf 1 0 0 1 50 {y} Tm ({_esc(text)}) Tj ET")
    stream = ("\n".join(ops) + "\n").encode("latin-1")
    objs: list[bytes] = [
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n",
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n",
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R"
        b"/Resources<</Font<</F1 5 0 R/F2 6 0 R/F3 7 0 R>>>>>>endobj\n",
        f"4 0 obj<</Length {len(stream)}>>stream\n".encode("latin-1") + stream + b"endstream\nendobj\n",
        b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n",
        b"6 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica-Bold>>endobj\n",
        b"7 0 obj<</Type/Font/Subtype/Type1/BaseFont/Courier>>endobj\n",
    ]
    pdf = b"%PDF-1.4\n"
    offsets = []
    for obj in objs:
        offsets.append(len(pdf))
        pdf += obj
    xref = len(pdf)
    pdf += b"xref\n0 8\n0000000000 65535 f \n"
    for off in offsets:
        pdf += f"{off:010d} 00000 n \n".encode("latin-1")
    pdf += b"trailer<</Size 8/Root 1 0 R>>\nstartxref\n" + str(xref).encode() + b"\n%%EOF"
    path.write_bytes(pdf)


def _counts_line(label: str, receipt: dict) -> str:
    return (f"{label}: chars={receipt['chars']} headings={receipt['md_headings']} "
            f"tables={receipt['md_tables']} fences={receipt['md_fences']} engine={receipt['engine']}")


def test_epub_markitdown_keeps_table_and_code(tmp_path: Path) -> None:
    if not _markitdown_available():
        pytest.skip("markitdown not installed in .tools/py (TS-4 install step)")
    src = tmp_path / "probe.epub"
    _write_epub(src)
    classic = extract_mod.extract(str(src), tmp_path / "w-classic", engine="classic")
    marked = extract_mod.extract(str(src), tmp_path / "w-marked", engine="markitdown")
    print(_counts_line("epub classic   ", classic))
    print(_counts_line("epub markitdown", marked))
    assert marked["engine"] == "markitdown"
    assert marked["md_headings"] >= 1 and marked["md_tables"] >= 2 and marked["md_fences"] >= 1
    assert classic["md_fences"] == 0 and classic["md_tables"] == 0
    assert classic["chars"] > 0 and marked["chars"] > 0


def test_pdf_markitdown_keeps_table_and_code(tmp_path: Path) -> None:
    if not _markitdown_available():
        pytest.skip("markitdown not installed in .tools/py (TS-4 install step)")
    src = tmp_path / "probe.pdf"
    _write_pdf(src)
    classic = extract_mod.extract(str(src), tmp_path / "w-classic", engine="classic")
    marked = extract_mod.extract(str(src), tmp_path / "w-marked", engine="markitdown")
    print(_counts_line("pdf classic    ", classic))
    print(_counts_line("pdf markitdown ", marked))
    assert marked["engine"] == "markitdown"
    assert marked["md_tables"] >= 2 and marked["md_fences"] >= 1
    assert classic["md_fences"] == 0 and classic["md_tables"] == 0
    classic_text = (tmp_path / "w-classic" / "full_text.txt").read_text(encoding="utf-8")
    assert "git status" in classic_text  # fallback still reads the words


def test_extract_rejects_unknown_engine(tmp_path: Path) -> None:
    src = tmp_path / "probe.txt"
    src.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError, match="engine"):
        extract_mod.extract(str(src), tmp_path / "w", engine="bogus")
