"""Chapter-aware split: headings become chapter files (BK-1005-1, EB-2026-10-05-S45).

Hunt basis (read live 2026-10-05, ideas only, no code copied): virgiliojr94
book-to-skill (MIT) plus asale-ai anything-to-skill (Apache-2.0) plus obra
superpowers (MIT) beat the 5k-char split. Take: fixed artifact SKILL plus
chapters plus glossary plus patterns plus cheatsheet with token budgets,
chapter detector with distinct count and 80-char title cap.

Reads ``workdir/full_text.txt``, finds Markdown (``#``) and AsciiDoc (``==``)
headings outside fenced blocks, and emits the fixed skill shape: SKILL.md
plus ``chapters/<nn>-<slug>.md`` plus glossary.md, patterns.md, cheatsheet.md.
Each chapter file holds a short head excerpt (like build.py chunk heads) so
the skill stays inside the token budgets in gates.py. Frontmatter and stubs
are reused from build.py: one home per concern, no second copy.

Wiring: call ``split_chapters(work, skill, name, description)`` directly for a
heading-structured source (progit sample: chapters match headings). The
classic ``split.split`` 5k-char chunks stay untouched: the index/eval path
pins them (test_split_chunk_sizes). Sources stay in git-ignored work/.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from . import build as build_mod

TITLE_CAP = 80
HEAD_CHARS = 600
SLUG_CAP = 50

HEADING_RE = re.compile(r"^(#{1,6}|={2,6})[ \t]+(\S.*)$")


# Fence close rule ported fresh from executablebooks/markdown-it-py (MIT,
# https://github.com/executablebooks/markdown-it-py/blob/master/markdown_it/rules_block/fence.py):
# ideas only -- min_markers=3, same-marker close, closing run >= opening run.
# No code copied; stdlib-only reimplementation for split_chapters.
def _fence_kind(line: str) -> tuple[str, int] | None:
    """(kind, run) of a block-delimiter line, or None.
    Markdown ```/~~~ fences: leading run of same marker, min 3.
    AsciiDoc ---- listing blocks and ==== example blocks: run of 4+."""
    s = line.strip()
    if not s:
        return None
    ch = s[0]
    if ch in ("`", "~"):
        n = 0
        for c in s:
            if c == ch:
                n += 1
            else:
                break
        if n < 3:
            return None
        return (ch * 3, n)
    if ch != "-" and ch != "=":
        return None
    if len(s) < 4:
        return None
    for c in s:
        if c != ch:
            return None
    return ("----" if ch == "-" else "====", len(s))


def is_fence(line: str) -> bool:
    """True for a block-delimiter line (any fence kind)."""
    return _fence_kind(line) is not None


def _headings_from_lines(lines: list[str]) -> list[tuple[int, str, int]]:
    """Single-pass scan: one _fence_kind call per line feeds fence+headings."""
    found: list[tuple[int, str, int]] = []
    open_fence: tuple[str, int] | None = None
    for lineno, line in enumerate(lines):
        info = _fence_kind(line)
        if info is not None:
            kind, n = info
            if open_fence is None:
                open_fence = info
            else:
                open_kind, open_n = open_fence
                if kind == open_kind and n >= open_n:
                    s = line.strip()
                    rest = s[n:].strip() if kind in ("```", "~~~") else ""
                    if rest == "":
                        open_fence = None
            continue
        if open_fence is not None:
            continue
        if line[:1] != "#" and line[:1] != "=":
            continue
        m = HEADING_RE.match(line)
        if not m:
            continue
        marks, title = m.group(1), m.group(2).strip()
        level = len(marks) if marks.startswith("#") else len(marks) - 1
        found.append((level, title[:TITLE_CAP].rstrip(), lineno))
    return found


def iter_headings(text: str) -> list[tuple[int, str, int]]:
    """Headings outside fenced blocks as (level, title, lineno) triples.

    Only the matching delimiter closes a block, so a merge-conflict
    ``=======`` line inside a ``----`` listing block stays hidden content.
    Closing run must reach the opening run (5-backtick open needs 5+ to
    close), so a short 3-backtick line inside a long fence stays content.
    """
    return _headings_from_lines(text.splitlines())


# Slug NFKD rule ported fresh from django/django (BSD-3-Clause,
# https://github.com/django/django/blob/main/django/utils/text.py slugify):
# ideas only -- unicodedata NFKD decompose plus ascii-ignore plus lower plus re.
# No code copied; stdlib-only reimplementation for split_chapters.
def slug(title: str) -> str:
    """Short file-safe slug for a chapter title."""
    out = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii").lower()).strip("-")
    return (out[:SLUG_CAP].rstrip("-") or "chapter")


def detect_chapters_from_lines(lines: list[str]) -> list[dict]:
    """One scan from already-split lines: no second splitlines, same rows."""
    rows: list[dict] = []
    seen: set[str] = set()
    for level, title, lineno in _headings_from_lines(lines):
        base = slug(title)
        name, n = base, 2
        while name in seen:
            name = f"{base}-{n}"
            n += 1
        seen.add(name)
        rows.append({"title": title, "level": level, "line": lineno, "slug": name})
    return rows


def detect_chapters(text: str) -> list[dict]:
    """One row per heading: title (80-char cap), level, line and a distinct slug."""
    return detect_chapters_from_lines(text.splitlines())


def split_chapters(workdir: Path, skilldir: Path, name: str, description: str,
                   head_chars: int = HEAD_CHARS) -> dict:
    """Split full_text.txt at its headings and write the fixed skill shape."""
    build_mod.validate_name(name, skilldir)
    text = (workdir / "full_text.txt").read_text(encoding="utf-8")
    lines = text.splitlines()
    chapters = detect_chapters_from_lines(lines)
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
    total_chars = 0
    for i, (start, end, ch) in enumerate(bounds, 1):
        if fell_back:
            body_lines = lines[start:end]
        elif start < ch["line"]:
            body_lines = lines[start:ch["line"]] + lines[ch["line"] + 1:end]
        else:
            body_lines = lines[start + 1:end]
        excerpt = "\n".join(body_lines).strip()[:head_chars].rstrip()
        content = f"## {ch['title']}\n\n{excerpt}\n"
        (outdir / f"{i:0{width}d}-{ch['slug']}.md").write_text(content, encoding="utf-8")
        total_chars += len(content)
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
