"""Extract stage: PDF/EPUB/DOCX/MD/TXT/URL to full_text.txt + metadata.json.

Engines (TS-4): --engine classic is the plain-text fallback (pypdf page join,
zipfile+BeautifulSoup body text, python-docx walk); --engine markitdown keeps
markdown structure (headings, pipe tables, fenced code) via markitdown
(Microsoft, MIT) with pdfplumber (MIT) table/code recovery on PDF;
--engine auto tries markitdown and falls back to classic with a receipt note.
markitdown lives in .tools/py (git-ignored, installed per TS-4), never
machine-wide; ebooklib is gone (classic EPUB needs only stdlib zipfile).
"""
from __future__ import annotations

import fnmatch
import json
import os
import random
import re
import sys
import time
import zipfile
from pathlib import Path


def _ensure_local_tools() -> None:
    """Put this repo's .tools/py first so the vendored markitdown resolves."""
    root = Path(__file__).resolve().parents[1] / ".tools" / "py"
    if root.is_dir() and str(root) not in sys.path:
        sys.path.insert(0, str(root))


ENGINES = ("classic", "markitdown", "auto")

# pdfplumber table/code recovery runs only under this page count; above it the
# markitdown PDF path keeps markitdown text and says so in the receipt.
_PDF_ENRICH_MAX_PAGES = 150

# Retry bound shaped by litl/backoff (MIT, https://github.com/litl/backoff/blob/main/backoff/_sync.py:
# max_tries/max_time/giveup/on_giveup; _wait_gen.py expo; _jitter.py full_jitter). Reimplemented here, not pasted.
def with_retry(fn, tries=3, giveup=(ValueError,), base=0.01, sleep=time.sleep, on_giveup=None):
    """Run fn() up to tries times; expo backoff with full jitter; giveup types fail fast."""
    last = None
    for attempt in range(1, tries + 1):
        try:
            return fn()
        except giveup as exc:
            exc.retry_tries = attempt
            if on_giveup is not None:
                on_giveup({"tries": attempt, "cause": exc})
            raise
        except Exception as exc:
            last = exc
            exc.retry_tries = attempt
            if attempt >= tries:
                if on_giveup is not None:
                    on_giveup({"tries": attempt, "cause": exc})
                raise
            sleep(random.uniform(0, base * (2 ** (attempt - 1))))
    raise last



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


# A docs folder (a manual kept as files, e.g. a docs repo checkout) is read file by file.
DOC_SUFFIXES = (".md", ".mdx", ".markdown", ".rst", ".txt")
_SKIP_DIRS = {"node_modules", "__pycache__", "export"}
_FRONT_MATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.S)


def _is_link(path: str) -> bool:
    isjunction = getattr(os.path, "isjunction", None)
    return os.path.islink(path) or bool(isjunction and isjunction(path))


def _read_folder(root: Path, workdir: Path, include: str | None = None) -> tuple[str, dict]:
    """Every doc file under root in path order, each under a `# file: <path>` line.

    Leaves out hidden folders, node_modules, export/ folders, links (a loop never ends) and the
    work dir itself when it sits inside root (a second run must not read its own output).
    include: an fnmatch pattern on the file name or the path under root, e.g. "about_*.md".
    """
    root = root.resolve()
    own = workdir.resolve()
    parts: list[str] = []
    skipped_own = 0
    for here, dirs, files in os.walk(root):
        keep = []
        for d in sorted(dirs):
            full = os.path.join(here, d)
            if Path(full).resolve() == own:
                skipped_own += 1
            elif d.startswith(".") or d in _SKIP_DIRS or _is_link(full):
                continue
            else:
                keep.append(d)
        dirs[:] = keep
        for name in sorted(files):
            if not name.lower().endswith(DOC_SUFFIXES) or name.startswith("."):
                continue
            rel = Path(os.path.join(here, name)).relative_to(root).as_posix()
            if include and not (fnmatch.fnmatch(name, include) or fnmatch.fnmatch(rel, include)):
                continue
            body = _read_text_file(Path(here) / name)
            body = _FRONT_MATTER.sub("", body, count=1).strip()
            if body:
                parts.append(f"# file: {rel}\n\n{body}")
    if not parts:
        raise ValueError(
            f"no {'/'.join(DOC_SUFFIXES)} files under {root}" + (f" matching {include!r}" if include else "")
        )
    return "\n\n".join(parts), {"files": len(parts), "skipped_own_output": skipped_own}


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_pdf_classic(path: Path) -> tuple[str, int]:
    """Per-page text in page order (pdf.js getTextContent pattern: idea only).

    Each page's items are read in content-stream order and pages are joined
    in index order, so the receipt can report per-page counts. pdfplumber
    (MIT) is the fallback when pypdf yields no text at all.
    """
    _ensure_local_tools()
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    if not any(p.strip() for p in pages):
        try:
            import pdfplumber

            with pdfplumber.open(str(path)) as pdf:
                pages = [(page.extract_text() or "") for page in pdf.pages]
        except Exception as exc:
            raise ValueError(f"classic pdfplumber fallback failed ({exc}); install .tools/py per TS-4") from exc
    return "\n".join(pages), len(pages)


def _md_table_row(cells: list[str]) -> str:
    cells = [(c or "").strip().replace("\n", " ") for c in cells]
    return "| " + " | ".join(cells) + " |"


# Lattice-only table recovery (idea from jsvine/pdfplumber, MIT licence,
# https://github.com/jsvine/pdfplumber: table_settings vertical/horizontal
# strategy "lines" finds ruled tables from vector lines/rects; reimplemented
# here, not pasted). Pages with no vector lines/rects skip both extract_tables
# and the Courier char scan, so text-only pages cost one lines/rects check.
_LATTICE_SETTINGS = {"vertical_strategy": "lines", "horizontal_strategy": "lines"}


def _page_has_vectors(page) -> bool:
    """True when the page draws at least one vector line or rect."""
    try:
        return bool(page.lines or page.rects)
    except Exception:
        return True


def _render_lattice_tables(page, blocks: list[str]) -> int:
    """Append pipe rows for one ruled page's lattice tables; returns new tables."""
    found = 0
    for table in page.extract_tables(table_settings=dict(_LATTICE_SETTINGS)) or []:
        rows = [[c or "" for c in row] for row in table if any((c or "").strip() for c in row)]
        if not rows:
            continue
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        blocks.append(_md_table_row(rows[0]))
        blocks.append("| " + " | ".join(["---"] * width) + " |")
        blocks.extend(_md_table_row(r) for r in rows[1:])
        found += 1
    return found


def _render_page_code(page, out: list[str]) -> int:
    """Append fenced blocks for one page's Courier lines; returns new fences."""
    lines: dict[tuple, list] = {}
    for ch in page.chars:
        key = round(float(ch["top"]))
        lines.setdefault(key, []).append(ch)
    fences = 0
    code_run: list[str] = []
    for key in sorted(lines):
        chars = sorted(lines[key], key=lambda c: float(c["x0"]))
        if not chars:
            continue
        mono = sum(1 for c in chars if "ourier" in str(c.get("fontname", "")))
        text = "".join(c.get("text", "") for c in chars).rstrip()
        if text and mono * 2 >= len(chars):
            code_run.append(text)
        elif code_run:
            out.append("```\n" + "\n".join(code_run) + "\n```")
            fences += 1
            code_run = []
    if code_run:
        out.append("```\n" + "\n".join(code_run) + "\n```")
        fences += 1
    return fences


def _pdf_tables_as_markdown(path: Path, max_pages: int) -> tuple[str, int, bool]:
    """pdfplumber lattice/line tables rendered as pipe rows (jsvine/pdfplumber, MIT).

    Returns (markdown, table_count, skipped). Skipped is True when the document
    exceeds max_pages; the caller records it instead of stalling a manual.
    """
    import pdfplumber

    with pdfplumber.open(str(path)) as pdf:
        if len(pdf.pages) > max_pages:
            return "", 0, True
        blocks: list[str] = []
        count = 0
        for page in pdf.pages:
            if not _page_has_vectors(page):
                continue
            count += _render_lattice_tables(page, blocks)
    if not blocks:
        return "", 0, False
    return "## Tables\n\n" + "\n".join(blocks), count, False


def _pdf_code_as_markdown(path: Path, max_pages: int) -> tuple[str, int, bool]:
    """Monospaced-font (Courier) lines grouped into fenced blocks via pdfplumber chars."""
    import pdfplumber

    with pdfplumber.open(str(path)) as pdf:
        if len(pdf.pages) > max_pages:
            return "", 0, True
        out: list[str] = []
        fences = 0
        for page in pdf.pages:
            if not _page_has_vectors(page):
                continue
            fences += _render_page_code(page, out)
    if not out:
        return "", 0, False
    return "## Code\n\n" + "\n\n".join(out), fences, False


def _read_pdf_markitdown(path: Path) -> tuple[str, dict]:
    """markitdown text plus pdfplumber table/code recovery (both MIT)."""
    _ensure_local_tools()
    from markitdown import MarkItDown

    import pdfplumber

    text = with_retry(lambda: MarkItDown(enable_builtins=True).convert(str(path)).text_content or "")
    with pdfplumber.open(str(path)) as pdf:
        pages = len(pdf.pages)
        if pages > _PDF_ENRICH_MAX_PAGES:
            tables_md, table_count, tables_skipped = "", 0, True
            code_md, fence_count, code_skipped = "", 0, True
        else:
            blocks: list[str] = []
            out: list[str] = []
            table_count = 0
            fence_count = 0
            for page in pdf.pages:
                if not _page_has_vectors(page):
                    continue
                table_count += _render_lattice_tables(page, blocks)
                fence_count += _render_page_code(page, out)
            tables_md = "## Tables\n\n" + "\n".join(blocks) if blocks else ""
            code_md = "## Code\n\n" + "\n\n".join(out) if out else ""
            tables_skipped = code_skipped = False
    extra = "\n\n".join(b for b in (tables_md, code_md) if b)
    info = {
        "pages": pages,
        "table_count": table_count,
        "tables_skipped": tables_skipped,
        "code_skipped": code_skipped,
    }
    return (text + ("\n\n" + extra if extra else "")).strip(), info


def _pdf_page_count(path: Path) -> int:
    from pypdf import PdfReader

    return len(PdfReader(str(path)).pages)


def _read_epub_classic(path: Path) -> tuple[str, list[dict]]:
    """Flattened body text via stdlib zipfile + BeautifulSoup (no ebooklib).

    Document files in archive order, <body> subtree only, script/style/nav
    dropped; pagebreak markers (epub:type/type == "pagebreak" or
    role == "doc-pagebreak") map to id/label pairs, label falling back
    text -> aria-label -> title -> doc heading -> id.
    """
    from bs4 import BeautifulSoup

    _NAV_TYPES = {"nav", "toc", "landmarks", "page-list"}
    parts: list[str] = []
    pages: list[dict] = []
    with zipfile.ZipFile(path) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith((".xhtml", ".html", ".htm"))]
        for name in sorted(names):
            soup = BeautifulSoup(zf.read(name), "html.parser")
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
                    pid = str(el.get("id") or "")
                    aria = str(el.get("aria-label") or "")
                    etitle = str(el.get("title") or "")
                    label = el.get_text(strip=True) or aria.strip() or etitle.strip() or title or pid
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


def _read_epub_markitdown(path: Path) -> tuple[str, dict]:
    """markitdown EPUB converter (_epub_converter.py, MIT): headings, tables, fences."""
    _ensure_local_tools()
    from markitdown import MarkItDown

    text = with_retry(lambda: MarkItDown(enable_builtins=True).convert(str(path)).text_content or "")
    return text, {}


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


def _read_docx_markitdown(path: Path) -> str:
    """markitdown DOCX converter: headings, tables and lists as markdown."""
    _ensure_local_tools()
    from markitdown import MarkItDown

    return with_retry(lambda: MarkItDown(enable_builtins=True).convert(str(path)).text_content or "")


def md_counts(text: str) -> dict:
    """Structure counts of extracted markdown: headings, table rows, fences."""
    lines = text.splitlines()
    headings = sum(1 for ln in lines if re.match(r"#{1,6} ", ln.strip()))
    tables = sum(1 for ln in lines if ln.strip().startswith("|") and ln.count("|") >= 2)
    fences = text.count("```") // 2
    return {"md_headings": headings, "md_tables": tables, "md_fences": fences}


def _use_markitdown(engine: str, suffix: str) -> bool:
    if engine == "markitdown":
        return suffix in (".pdf", ".epub", ".docx")
    if engine == "auto":
        return suffix in (".pdf", ".epub", ".docx")
    return False


def extract(src: str, workdir: Path, strip_gutenberg: bool = True, include: str | None = None,
            engine: str = "classic") -> dict:
    if engine not in ENGINES:
        raise ValueError(f"--engine {engine} unknown: pick classic, markitdown or auto")
    if not re.match(r"https?://", src) and not Path(src).exists():
        raise ValueError(f"--in {src} not found: give a file or a docs folder")
    workdir.mkdir(parents=True, exist_ok=True)
    engine_used = "classic"
    enrich: dict = {}
    if re.match(r"https?://", src):
        import urllib.request  # lazy: URL-only so --help and file runs skip http/ssl
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
        if path.is_dir():
            text, folder_meta = _read_folder(path, workdir, include)
            kind, strip_gutenberg = "folder", False
        elif suffix == ".pdf":
            if _use_markitdown(engine, suffix):
                try:
                    text, enrich = _read_pdf_markitdown(path)
                    pages, kind, engine_used = enrich.pop("pages", 0), "pdf", "markitdown"
                except Exception as exc:
                    if engine == "markitdown":
                        raise ValueError(f"markitdown PDF failed ({exc}); install .tools/py per TS-4") from exc
                    text, pages = _read_pdf_classic(path)
                    kind, engine_used = "pdf", "classic-fallback"
                    enrich = {"note": "markitdown failed after {} tries: {}".format(getattr(exc, "retry_tries", 3), exc)}
            else:
                text, pages = _read_pdf_classic(path)
                kind = "pdf"
        elif suffix == ".epub":
            if _use_markitdown(engine, suffix):
                try:
                    text, enrich = _read_epub_markitdown(path)
                    pages, kind, engine_used = [], "epub", "markitdown"
                except Exception as exc:
                    if engine == "markitdown":
                        raise ValueError(f"markitdown EPUB failed ({exc}); install .tools/py per TS-4") from exc
                    text, pages = _read_epub_classic(path)
                    kind, engine_used = "epub", "classic-fallback"
                    enrich = {"note": "markitdown failed after {} tries: {}".format(getattr(exc, "retry_tries", 3), exc)}
            else:
                text, pages = _read_epub_classic(path)
                kind = "epub"
        elif suffix == ".docx":
            if _use_markitdown(engine, suffix):
                try:
                    text, kind, engine_used = _read_docx_markitdown(path), "docx", "markitdown"
                except Exception as exc:
                    if engine == "markitdown":
                        raise ValueError(f"markitdown DOCX failed ({exc}); install .tools/py per TS-4") from exc
                    text, kind, engine_used = _read_docx(path), "docx", "classic-fallback"
                    enrich = {"note": "markitdown failed after {} tries: {}".format(getattr(exc, "retry_tries", 3), exc)}
            else:
                text, kind = _read_docx(path), "docx"
        else:
            text, kind = _read_text_file(path), "text"
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    stripped = False
    if strip_gutenberg:
        text, stripped = strip_gutenberg_markers(text)
    (workdir / "full_text.txt").write_text(text, encoding="utf-8")
    meta = {"source": src, "kind": kind, "chars": len(text), "stripped": stripped,
            "engine_requested": engine, "engine": engine_used, **md_counts(text)}
    if kind == "folder":
        meta.update(folder_meta)
    if pages is not None:
        meta["pages"] = pages
    meta.update({k: v for k, v in enrich.items() if k != "pages"})
    (workdir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    receipt = {"stage": "extract", **meta}
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt

