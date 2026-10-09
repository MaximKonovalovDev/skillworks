"""Every file path named in docs/VIDEO-PACK.md must exist."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "VIDEO-PACK.md"

PATH_RE = re.compile(r"(packs/[A-Za-z0-9_\-./]+|skills/[A-Za-z0-9_\-./]+|docs/[A-Za-z0-9_\-./]+|evals/[A-Za-z0-9_\-./]+)")


def _doc_paths():
    text = DOC.read_text(encoding="utf-8")
    found = PATH_RE.findall(text)
    cleaned = []
    for raw in found:
        path = raw.rstrip(".,;:)```''\"")
        cleaned.append(path)
    return text, sorted(set(cleaned))


def test_doc_exists():
    assert DOC.exists(), "docs/VIDEO-PACK.md is missing"


def test_every_named_path_exists():
    text, paths = _doc_paths()
    assert paths, "doc names no file paths"
    missing = [p for p in paths if not (ROOT / p).exists()]
    assert not missing, f"doc names files that do not exist: {missing}"


def test_stale_paths_are_gone():
    text = DOC.read_text(encoding="utf-8")
    for stale in ("packs/video/pack.json", "skills/cut", "skills/voice", "skills/publish", "video-pack.zip"):
        assert stale not in text, f"stale reference still in doc: {stale}"
