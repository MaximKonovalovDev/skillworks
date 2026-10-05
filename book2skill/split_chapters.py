"""Chapter-aware split: headings become chapter files (BK-1005-1).

Reads ``workdir/full_text.txt``, finds Markdown (``#``) and AsciiDoc (``==``)
headings outside fenced blocks, and emits the fixed skill shape: SKILL.md
plus ``chapters/<nn>-<slug>.md`` plus glossary.md, patterns.md, cheatsheet.md.
Each chapter file holds a short head excerpt (like build.py chunk heads) so
the skill stays inside the token budgets in gates.py. Frontmatter and stubs
are reused from build.py: one home per concern, no second copy.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import build as build_mod

TITLE_CAP = 80
HEAD_CHARS = 600
SLUG_CAP = 50

HEADING_RE = re.compile(r"^(#{1,6}|={2,6})[ \t]+(\S.*)$")


def _fence_kind(line: str) -> str | None:
    """Block-delimiter kind of the line, or None: Markdown ```/~~~ fences,
    AsciiDoc ---- listing blocks and ==== example blocks."""
    s = line.strip()
    if s.startswith("```") or s.startswith("~~~"):
        return s[:3]
    if len(s) >= 4 and set(s) == {"-"}:
        return "----"
    if len(s) >= 4 and set(s) == {"="}:
        return "===="
    return None


def is_fence(line: str) -> bool:
    """True for a block-delimiter line (any fence kind)."""
    return _fence_kind(line) is not None


def iter_headings(text: str) -> list[tuple[int, str, int]]:
    """Headings outside fenced blocks as (level, title, lineno) triples.

    Only the matching delimiter closes a block, so a merge-conflict
    ``=======`` line inside a ``----`` listing block stays hidden content.
    """
    found: list[tuple[int, str, int]] = []
    open_fence: str | None = None
    for lineno, line in enumerate(text.splitlines()):
        kind = _fence_kind(line)
        if kind is not None:
            if open_fence is None:
                open_fence = kind
            elif kind == open_fence:
                open_fence = None
            continue
        if open_fence is not None:
            continue
        m = HEADING_RE.match(line)
        if not m:
            continue
        marks, title = m.group(1), m.group(2).strip()
        level = len(marks) if marks.startswith("#") else len(marks) - 1
        found.append((level, title[:TITLE_CAP].rstrip(), lineno))
    return found


def slug(title: str) -> str:
    """Short file-safe slug for a chapter title."""
    out = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return (out[:SLUG_CAP].rstrip("-") or "chapter")


def detect_chapters(text: str) -> list[dict]:
    """One row per heading: title (80-char cap), level, line and a distinct slug."""
    rows: list[dict] = []
    seen: set[str] = set()
    for level, title, lineno in iter_headings(text):
        base = slug(title)
        name, n = base, 2
        while name in seen:
            name = f"{base}-{n}"
            n += 1
        seen.add(name)
        rows.append({"title": title, "level": level, "line": lineno, "slug": name})
    return rows


def split_chapters(workdir: Path, skilldir: Path, name: str, description: str,
                   head_chars: int = HEAD_CHARS) -> dict:
    """Split full_text.txt at its headings and write the fixed skill shape."""
    build_mod.validate_name(name, skilldir)
    text = (workdir / "full_text.txt").read_text(encoding="utf-8")
    lines = text.splitlines()
    chapters = detect_chapters(text)
    fell_back = not chapters
    if fell_back:
        chapters = [{"title": "Notes", "level": 1, "line": 0, "slug": "notes"}]
        bounds = [(0, len(lines), chapters[0])]
    else:
        bounds = []
        for i, ch in enumerate(chapters):
            start = ch["line"] if i else 0
            end = chapters[i + 1]["line"] if i + 1 < len(chapters) else len(lines)
            bounds.append((start, end, ch))
    outdir = skilldir / "chapters"
    outdir.mkdir(parents=True, exist_ok=True)
    width = max(2, len(str(len(bounds))))
    for i, (start, end, ch) in enumerate(bounds, 1):
        if fell_back:
            body_lines = lines[start:end]
        elif start < ch["line"]:
            body_lines = lines[start:ch["line"]] + lines[ch["line"] + 1:end]
        else:
            body_lines = lines[start + 1:end]
        excerpt = "\n".join(body_lines).strip()[:head_chars].rstrip()
        (outdir / f"{i:0{width}d}-{ch['slug']}.md").write_text(
            f"## {ch['title']}\n\n{excerpt}\n", encoding="utf-8")
    noncommercial = build_mod.is_noncommercial_text(description)
    licence = build_mod.NC_LICENSE if noncommercial else "MIT"
    skilldir.mkdir(parents=True, exist_ok=True)
    (skilldir / "SKILL.md").write_text(
        build_mod._frontmatter(name, description, licence=licence)
        + build_mod._scaffold_body(name),
        encoding="utf-8",
    )
    for fname, stub in build_mod.STUB_FILES.items():
        (skilldir / fname).write_text(stub, encoding="utf-8")
    total_chars = sum(len((outdir / p).read_text(encoding="utf-8")) for p in sorted(outdir.iterdir()))
    receipt = {
        "stage": "split_chapters",
        "skill": str(skilldir),
        "chapters": len(bounds),
        "distinct": len({ch["slug"] for _, _, ch in bounds}),
        "title_cap": TITLE_CAP,
        "chapter_chars": total_chars,
        "chapter_tokens": total_chars // 4 + 10,
        "noncommercial": noncommercial,
        "prompt": build_mod.prompt_version(),
        "layout": "skill-pack",
    }
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt
