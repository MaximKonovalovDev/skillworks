"""Extract stage: PDF/EPUB/DOCX/MD/TXT/URL to full_text.txt + metadata.json."""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _read_epub(path: Path) -> str:
    import ebooklib
    from bs4 import BeautifulSoup
    from ebooklib import epub

    book = epub.read_epub(str(path))
    parts: list[str] = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            parts.append(soup.get_text("\n"))
    return "\n".join(parts)


def _read_docx(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def extract(src: str, workdir: Path) -> dict:
    workdir.mkdir(parents=True, exist_ok=True)
    if re.match(r"https?://", src):
        req = urllib.request.Request(src, headers={"User-Agent": "skillworks/0.1"})
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
            raw = resp.read().decode("utf-8", errors="replace")
        from bs4 import BeautifulSoup

        text = BeautifulSoup(raw, "html.parser").get_text("\n")
        kind = "url"
    else:
        path = Path(src)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            text, kind = _read_pdf(path), "pdf"
        elif suffix == ".epub":
            text, kind = _read_epub(path), "epub"
        elif suffix == ".docx":
            text, kind = _read_docx(path), "docx"
        else:
            text, kind = _read_text_file(path), "text"
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    (workdir / "full_text.txt").write_text(text, encoding="utf-8")
    meta = {"source": src, "kind": kind, "chars": len(text)}
    (workdir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    receipt = {"stage": "extract", **meta}
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt
