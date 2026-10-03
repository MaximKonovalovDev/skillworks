"""Extract stage: PDF/EPUB/DOCX/MD/TXT/URL to full_text.txt + metadata.json."""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path


# Gutenberg header/footer markers (idea from kiasar/gutenberg_cleaner, MIT:
# strip_headers.py TEXT_START/END_MARKERS; reimplemented here, not pasted).
# Header reset applies only when a start marker hits in the first 600 lines;
# footer break applies only after line 100, so body mentions never cut text.
TEXT_START_MARKERS = (
    "*** START OF THE PROJECT GUTENBERG",
    "*** START OF THIS PROJECT GUTENBERG",
)

TEXT_END_MARKERS = (
    "*** END OF THE PROJECT GUTENBERG",
    "*** END OF THIS PROJECT GUTENBERG",
)

_START_SCAN_LINES = 600
_END_MIN_LINE = 100


def strip_gutenberg_markers(text: str) -> tuple[str, bool]:
    """Cut PG header/footer by marker lists; plain fallback when absent."""
    lines = text.splitlines()
    start = 0
    for i, line in enumerate(lines[:_START_SCAN_LINES]):
        if any(m in line for m in TEXT_START_MARKERS):
            start = i + 1
            break
    else:
        return text, False
    end = len(lines)
    stripped_end = False
    for j in range(start, len(lines)):
        if j >= _END_MIN_LINE and any(m in lines[j] for m in TEXT_END_MARKERS):
            end = j
            stripped_end = True
            break
    body = "\n".join(lines[start:end]).strip()
    return body, True if (start > 0 or stripped_end) else False


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_pdf(path: Path) -> tuple[str, int]:
    """Per-page text in page order (pdf.js getTextContent pattern: idea only).

    Each page's items are read in content-stream order and pages are joined
    in index order, so the receipt can report per-page counts.
    """
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(pages), len(pages)


def _read_epub(path: Path) -> tuple[str, list[dict]]:
    """Body-subtree text + pagebreak-label map (ideas-only, AGPL never pasted).

    Body-only: parse each document item and read only the <body> subtree,
    dropping <head> chrome plus in-body <nav>/script/style and nav-typed
    elements. Page map: scan the body for pagebreak markers
    (epub:type/type == "pagebreak" or role == "doc-pagebreak"); label
    falls back text -> aria-label -> title -> doc heading (first
    non-empty h1..h6) -> id.
    """
    import ebooklib
    from bs4 import BeautifulSoup
    from ebooklib import epub

    _NAV_TYPES = {"nav", "toc", "landmarks", "page-list"}

    book = epub.read_epub(str(path))
    parts: list[str] = []
    pages: list[dict] = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            root = soup.body if soup.body is not None else soup
            title = ""
            for tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                head = root.find(tag)
                if head is not None and head.get_text(strip=True):
                    title = head.get_text(strip=True)
                    break
            for el in root.find_all(True):
                ptype = el.get("epub:type") or el.get("type") or ""
                if isinstance(ptype, list):
                    ptype = " ".join(ptype)
                role = el.get("role") or ""
                if isinstance(role, list):
                    role = " ".join(role)
                if str(ptype).strip().lower() == "pagebreak" or str(role).strip().lower() == "doc-pagebreak":
                    pid = el.get("id") or ""
                    if isinstance(pid, list):
                        pid = " ".join(pid)
                    pid = str(pid)
                    aria = el.get("aria-label") or ""
                    if isinstance(aria, list):
                        aria = " ".join(aria)
                    etitle = el.get("title") or ""
                    if isinstance(etitle, list):
                        etitle = " ".join(etitle)
                    label = (
                        el.get_text(strip=True)
                        or str(aria).strip()
                        or str(etitle).strip()
                        or title
                        or pid
                    )
                    pages.append({"id": pid, "label": label})
            for bad in root.find_all(["script", "style", "nav"]):
                bad.decompose()
            for bad in root.find_all(attrs={"epub:type": True}):
                val = bad.get("epub:type") or ""
                if isinstance(val, list):
                    val = " ".join(val)
                if str(val).strip().lower() in _NAV_TYPES:
                    bad.decompose()
            parts.append(root.get_text("\n"))
    return "\n".join(parts), pages


def _read_docx(path: Path) -> str:
    """Paragraph + table walk in document order (python-docx pattern: idea only)."""
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(str(path))
    parts: list[str] = []
    for child in doc.element.body.iterchildren():
        if child.tag.endswith("}p"):
            text = Paragraph(child, doc).text.strip()
            if text:
                parts.append(text)
        elif child.tag.endswith("}tbl"):
            for row in Table(child, doc).rows:
                cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if cells:
                    parts.append(" | ".join(cells))
    return "\n".join(parts) if parts else "\n".join(p.text for p in doc.paragraphs)


def extract(src: str, workdir: Path, strip_gutenberg: bool = True) -> dict:
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
        pages: int | list | None = None
        if suffix == ".pdf":
            text, pages = _read_pdf(path)
            kind = "pdf"
        elif suffix == ".epub":
            text, epub_pages = _read_epub(path)
            pages, kind = epub_pages, "epub"
        elif suffix == ".docx":
            text, kind = _read_docx(path), "docx"
        else:
            text, kind = _read_text_file(path), "text"
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    stripped = False
    if strip_gutenberg:
        text, stripped = strip_gutenberg_markers(text)
    (workdir / "full_text.txt").write_text(text, encoding="utf-8")
    meta = {"source": src, "kind": kind, "chars": len(text), "stripped": stripped}
    if pages is not None:
        meta["pages"] = pages
    (workdir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    receipt = {"stage": "extract", **meta}
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt
