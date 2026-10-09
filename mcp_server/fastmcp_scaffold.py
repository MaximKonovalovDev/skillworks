"""FastMCP-style scaffold for one EPUB tool: list_chapters.

Stdlib only, no network, no auth. Shape follows the PrefectHQ/fastmcp
pattern (Apache-2.0, ideas only, no paste): a FastMCP app with one
@mcp.tool whose input schema is derived from the function signature
(the same trick as mcp_server/server.py _input_schema).

When the real `fastmcp` package is installed this module registers on it;
otherwise it uses a tiny local shim with the same `.tool` decorator shape,
so swapping backends changes nothing about the tool.
"""
from __future__ import annotations

# Cold-start is stdlib-shim fast: xml/path/inspect stay lazy inside functions.

TOOL_NAME = "list_chapters"
TOOL_DESCRIPTION = (
    "List chapters of an unpacked EPUB directory in spine (reading) order. "
    "Use to get the table of contents before extracting a section."
)

BACKEND = "fastmcp"

try:  # PrefectHQ/fastmcp (Apache-2.0) when installed
    from fastmcp import FastMCP
except ImportError:  # stdlib-only fallback: same .tool shape
    BACKEND = "stdlib-shim"

    class FastMCP:  # noqa: D101 - minimal decorator shim, same .tool shape
        def __init__(self, name: str) -> None:
            self.name = name
            self.tools: dict = {}

        def tool(self, fn=None, **kwargs):
            def deco(f):
                self.tools[f.__name__] = f
                return f

            return deco(fn) if callable(fn) else deco


mcp = FastMCP("skillworks-epub")

CHAPTER_EXTS = (".xhtml", ".html", ".htm")
CONTAINER_PATH = "META-INF/container.xml"

_DESCRIPTIONS = {
    "epub_dir": "Path to an unpacked EPUB directory (folder with *.opf, not the .epub zip).",
}


def _local(tag: str) -> str:
    """Strip the XML namespace from a tag name."""
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _prettify(stem: str) -> str:
    return stem.replace("_", " ").replace("-", " ").strip().title() or stem


def _find_opf(epub: Path) -> Path | None:
    """Locate the OPF package file: container.xml first, else first *.opf."""
    import xml.etree.ElementTree as ET  # lazy: keep cold import fast
    container = epub / CONTAINER_PATH
    if container.is_file():
        try:
            root = ET.parse(str(container)).getroot()
        except (ET.ParseError, OSError):
            root = None
        if root is not None:
            for el in root.iter():
                if _local(el.tag) == "rootfile":
                    cand = epub / (el.get("full-path") or "")
                    if cand.suffix.lower() == ".opf" and cand.is_file():
                        return cand
    opfs = sorted(epub.rglob("*.opf"))
    return opfs[0] if opfs else None


def _ncx_labels(ncx: Path) -> dict[str, str]:
    """Map content src -> nav label from an NCX file (empty when unreadable)."""
    import xml.etree.ElementTree as ET  # lazy: keep cold import fast
    labels: dict[str, str] = {}
    try:
        root = ET.parse(str(ncx)).getroot()
    except (ET.ParseError, OSError):
        return labels
    for node in root.iter():
        if _local(node.tag) != "navPoint":
            continue
        label, src = "", ""
        for child in node:
            kind = _local(child.tag)
            if kind == "navLabel" and not label:
                label = "".join(child.itertext()).strip()
            elif kind == "content" and not src:
                src = (child.get("src") or "").split("#")[0].strip()
        if src and label:
            labels.setdefault(src.replace("\\", "/"), label)
    return labels


def _rel(epub: Path, base: Path, href: str) -> str:
    """Href as a posix path relative to the EPUB root when possible."""
    try:
        return (base / href).relative_to(epub).as_posix()
    except ValueError:
        return href.replace("\\", "/")


def _spine_chapters(epub: Path, opf: Path) -> list[dict] | None:
    """Chapters in spine order with NCX titles. None when no spine to follow."""
    import xml.etree.ElementTree as ET  # lazy: keep cold import fast
    from pathlib import Path  # lazy: keep cold import fast
    try:
        root = ET.parse(str(opf)).getroot()
    except (ET.ParseError, OSError):
        return None
    base = opf.parent
    manifest: dict[str, str] = {}
    for el in root.iter():
        if _local(el.tag) == "item":
            iid, href = el.get("id"), el.get("href")
            if iid and href:
                manifest[iid] = href.split("#")[0].strip()
    order = [el.get("idref") for el in root.iter() if _local(el.tag) == "itemref"]
    order = [i for i in order if i in manifest]
    if not order:
        return None
    labels: dict[str, str] = {}
    for path in base.glob("*.ncx"):
        labels.update(_ncx_labels(path))
    for iid in order:
        cand = base / manifest[iid]
        if cand.suffix.lower() == ".ncx" and cand.is_file():
            labels.update(_ncx_labels(cand))
    chapters = []
    for iid in order:
        href = manifest[iid]
        if href.lower().endswith(".ncx"):
            continue
        norm = href.replace("\\", "/")
        chapters.append(
            {
                "index": len(chapters),
                "id": iid,
                "href": _rel(epub, base, href),
                "title": labels.get(norm, _prettify(Path(href).stem)),
            }
        )
    return chapters or None


def _fallback_chapters(epub: Path) -> list[dict]:
    """Sorted chapter files when no OPF spine exists (never META-INF)."""
    files = sorted(
        (
            p
            for p in epub.rglob("*")
            if p.is_file()
            and p.suffix.lower() in CHAPTER_EXTS
            and "META-INF" not in p.parts
        ),
        key=lambda p: p.relative_to(epub).as_posix(),
    )
    return [
        {
            "index": n,
            "id": p.stem,
            "href": p.relative_to(epub).as_posix(),
            "title": _prettify(p.stem),
        }
        for n, p in enumerate(files)
    ]


@mcp.tool
def list_chapters(epub_dir: str) -> list[dict]:
    """List chapters of an unpacked EPUB directory in reading order."""
    if not isinstance(epub_dir, str) or not epub_dir.strip():
        raise ValueError("epub_dir is required (non-empty string)")
    from pathlib import Path  # lazy: keep cold import fast
    epub = Path(epub_dir).expanduser()
    if not epub.exists():
        raise ValueError(f"epub_dir not found: {epub_dir!r}")
    if not epub.is_dir():
        raise ValueError(f"epub_dir is not a directory: {epub_dir!r}")
    opf = _find_opf(epub)
    if opf is not None:
        chapters = _spine_chapters(epub, opf)
        if chapters:
            return chapters
    return _fallback_chapters(epub)


def _input_schema() -> dict:
    """Derive list_chapters inputSchema from its signature (server.py trick)."""
    import inspect  # lazy: keep cold import fast
    sig = inspect.signature(list_chapters)
    props: dict = {}
    required: list = []
    for name, param in sig.parameters.items():
        props[name] = {"type": "string", "description": _DESCRIPTIONS.get(name, name)}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": props, "required": required}


INPUT_SCHEMA = _input_schema()

TOOL = {
    "name": TOOL_NAME,
    "description": TOOL_DESCRIPTION,
    "inputSchema": INPUT_SCHEMA,
}


def _validate_list_chapters_args(args) -> tuple[bool, dict | str]:
    """Validate tool arguments. Returns (ok, cleaned|message)."""
    if not isinstance(args, dict):
        return False, "arguments must be an object with epub_dir"
    epub_dir = args.get("epub_dir")
    if not isinstance(epub_dir, str) or not epub_dir.strip():
        return False, "epub_dir is required (non-empty string)"
    return True, {"epub_dir": epub_dir}


__all__ = [
    "BACKEND",
    "INPUT_SCHEMA",
    "TOOL",
    "TOOL_DESCRIPTION",
    "TOOL_NAME",
    "list_chapters",
    "mcp",
]
