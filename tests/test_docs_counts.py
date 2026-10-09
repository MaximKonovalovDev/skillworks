"""Docs skill-count guard: docs must not pin a rotting exact count."""
"""skills/ is the source of truth. Fails on stale 66 or 59 and on missing paths."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "INDEX.md"
README = ROOT / "skills" / "README.md"
STALE = ["66", "59"]

def _read(p):
    return p.read_text(encoding="utf-8")

def test_no_stale_exact_counts():
    index_text = _read(INDEX)
    readme_text = _read(README)
    for stale in STALE:
        assert stale not in index_text, "stale count still in docs/INDEX.md"
        assert stale not in readme_text, "stale count still in skills/README.md"
    assert "skills/" in index_text
    assert "skills/" in readme_text
    assert re.search("70", index_text + readme_text), "docs must point at skills/"
    assert not re.search("[0-9]+ +skill folders", index_text), "docs/INDEX.md pins an exact count again"
    assert not re.search("[0-9]+ +skill folders", readme_text), "skills/README.md pins an exact count again"

def _candidates(text):
    spans = re.findall("`([^`]+)`", text)
    out = []
    for s in spans:
        s = s.strip()
        if not s:
            continue
        if " " in s or "<" in s or ">" in s or "*" in s or "|" in s:
            continue
        if "->" in s:
            continue
        if "/" not in s and not s.endswith((".md", ".py", ".json", ".jsonl", ".csv", ".txt")):
            continue
        if s in ("references/", "scripts/"):
            continue
        out.append(s)
    seen = sorted(set(out))
    return seen

def test_every_path_docs_name_exists():
    index_text = _read(INDEX)
    readme_text = _read(README)
