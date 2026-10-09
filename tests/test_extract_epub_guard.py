"""Guard: nested toc containing pagebreak must not crash classic EPUB reader.

Klabnik repro: OEBPS/xhtml/contents.xhtml has <section epub:type="toc">
containing <span epub:type="pagebreak">. Decomposing the parent section
clears children's attrs, so a later bad.get() crashed with
AttributeError NoneType.get at element.py self.attrs.get.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

from book2skill import extract as extract_mod


def _write_epub(path: Path, docs: dict[str, str]) -> None:
    items = "".join(
        f'<item id="d{i}" href="{name}" media-type="application/xhtml+xml"/>'
        for i, name in enumerate(sorted(docs))
    )
    refs = "".join(f'<itemref idref="d{i}"/>' for i in range(len(docs)))
    opf = (
        '<?xml version="1.0"?><package version="3.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="b">'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Fixture</dc:title>'
        '<dc:identifier id="b">fixture</dc:identifier><dc:language>en</dc:language></metadata>'
        f"<manifest>{items}</manifest><spine>{refs}</spine></package>"
    )
    container = (
        '<?xml version="1.0"?><container version="1.0" '
        'xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
        '<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
        "</rootfiles></container>"
    )
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip")
        zf.writestr("META-INF/container.xml", container)
        zf.writestr("OEBPS/content.opf", opf)
        for name, body in sorted(docs.items()):
            zf.writestr(f"OEBPS/{name}", body)


def test_nested_toc_pagebreak_no_crash(tmp_path: Path) -> None:
    """(a) nested toc with pagebreak child: pages kept, toc text gone, body kept."""
    src = tmp_path / "nested.epub"
    _write_epub(src, {"ch1.xhtml": (
        "<html xmlns:epub='http://www.idpf.org/2007/ops'><head>"
        "<title>Nested Fixture</title></head><body>"
        "<section epub:type='toc'><span epub:type='pagebreak' id='pg_ix' aria-label='ix'/>"
        "<ol><li>TOCSECRET-NAV</li></ol></section>"
        "<h1>Body Heading BODYSECRET-HEAD</h1>"
        "<p>Body paragraph BODYSECRET-TEXT.</p>"
        "</body></html>"
    )})
    work = tmp_path / "work"
    receipt = extract_mod.extract(str(src), work, engine="classic")
    assert receipt["kind"] == "epub"
    assert {"id": "pg_ix", "label": "ix"} in receipt["pages"]
    text = (work / "full_text.txt").read_text(encoding="utf-8")
    assert "BODYSECRET-HEAD" in text and "BODYSECRET-TEXT" in text
    assert "TOCSECRET-NAV" not in text


def test_decomposed_tag_skipped(tmp_path: Path) -> None:
    """(b) already-decomposed child is skipped via _epub_attr, never raises."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(
        "<body><section epub:type='toc'><span epub:type='pagebreak' id='c1'>7</span></section></body>",
        "html.parser",
    )
    parent = soup.find("section")
    child = soup.find("span")
    assert parent is not None and child is not None
    parent.decompose()
    # direct child read after parent decompose must not raise
    assert extract_mod._epub_attr(child, "epub:type") == ""
    assert extract_mod._epub_attr(None, "epub:type") == ""
    assert extract_mod._epub_attr(object(), "epub:type") == ""
    # full reader on the same nested shape also survives (crafted epub)
    src = tmp_path / "decomp.epub"
    _write_epub(src, {"ch1.xhtml": (
        "<html xmlns:epub='http://www.idpf.org/2007/ops'><head>"
        "<title>Decomp Fixture</title></head><body>"
        "<section epub:type='toc'><span epub:type='pagebreak' id='p9'>9</span>"
        "TOCSECRET-TWO</section>"
        "<p>Body BODYSECRET-TWO.</p>"
        "</body></html>"
    )})
    receipt = extract_mod.extract(str(src), tmp_path / "work2", engine="classic")
    assert {"id": "p9", "label": "9"} in receipt["pages"]
    text = (tmp_path / "work2" / "full_text.txt").read_text(encoding="utf-8")
    assert "BODYSECRET-TWO" in text
    assert "TOCSECRET-TWO" not in text
