"""Build stage: two-pass notes-then-skill scaffold.

Pass 1 condenses chunk heads into notes. Pass 2 writes the skill scaffold:
SKILL.md with spec frontmatter plus chapters, glossary, patterns, cheatsheet.
An LLM pass can enrich notes later; the scaffold is always valid alone.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .extract import TEXT_END_MARKERS, TEXT_START_MARKERS, strip_gutenberg_markers

PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "build-skill.md"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_RULE = "name matches dir, a-z0-9- only"


# K-48 slice (1): a NonCommercial source can never get a price. Hints match the
# Creative-Commons NonCommercial markers (BY-NC, -NC-, NC-SA) and the word
# itself; ordinary prose ("price", "sold", "$10") never matches.
NC_HINTS = ("noncommercial", "by-nc", "-nc-", "nc-sa")

# An NC skill's scaffold licence (K-48): the MIT line is for commercial sources only.
NC_LICENSE = "CC-BY-NC-SA-3.0 (source; NonCommercial, never sold)"

_PRICE_RE = re.compile(r"\$\d")


def is_noncommercial_text(text: str) -> bool:
    """True when the text names a NonCommercial source licence."""
    low = text.lower()
    return any(h in low for h in NC_HINTS)


def skill_is_noncommercial(skilldir: Path) -> bool:
    """True when the skill's own files say its source is NonCommercial."""
    for rel in ("SKILL.md", "references/sources.md"):
        try:
            if is_noncommercial_text((skilldir / rel).read_text(encoding="utf-8")):
                return True
        except OSError:
            continue
    return False


def find_price_markers(skilldir: Path) -> list[str]:
    """Structured price carriers inside the skill (price.txt, pack.json, a listing Price $N line).

    Free-text mentions (a Vol 0 sample line, prose about prices) are not
    markers: slice (2) removes the paid-Vol-1 line, this gate stops a priced pack.
    """
    marks: list[str] = []
    try:
        if (skilldir / "price.txt").is_file() and _PRICE_RE.search(
            (skilldir / "price.txt").read_text(encoding="utf-8")
        ):
            marks.append("price.txt names a price")
    except OSError:
        pass
    try:
        if (skilldir / "pack.json").is_file():
            data = json.loads((skilldir / "pack.json").read_text(encoding="utf-8"))
            price = data.get("price_usd")
            if isinstance(price, (int, float)) and price > 0:
                marks.append(f"pack.json price_usd {price:g}")
    except (OSError, ValueError):
        pass
    try:
        if (skilldir / "listing.md").is_file():
            for line in (skilldir / "listing.md").read_text(encoding="utf-8").splitlines():
                if line.strip().lower().startswith(("- price", "price")) and _PRICE_RE.search(line):
                    marks.append(f"listing.md prices it ({line.strip()[:60]})")
                    break
    except OSError:
        pass
    return marks


def refuse_nc_price(skilldir: Path) -> None:
    """Refuse a price on a NonCommercial source (K-48 slice 1); free NC skills pass."""
    if skill_is_noncommercial(skilldir):
        marks = find_price_markers(skilldir)
        if marks:
            raise SystemExit(
                f"export refused: NonCommercial source '{skilldir.name}' can never get a price "
                f"({'; '.join(marks)}); share it free under the same licence"
            )


def validate_name(name: str, skilldir: Path) -> None:
    """Refuse a --name that breaks the skill naming rule (016)."""
    if not NAME_RE.match(name):
        raise ValueError(f"--name '{name}' is invalid (rule: {NAME_RULE})")
    if name != skilldir.name:
        raise ValueError(f"--name '{name}' must match skill dir '{skilldir.name}' (rule: {NAME_RULE})")


# The scaffold's placeholder files. A file that still equals its placeholder has no author yet.
STUB_FILES = {
    "glossary.md": "# Glossary\n\nFill terms while reading.\n",
    "patterns.md": "# Patterns\n\nFill reusable patterns while reading.\n",
    "cheatsheet.md": "# Cheatsheet\n\nFill one-page recall while reading.\n",
}


# Gutenberg boilerplate that survives in stale chunks (K-48). Chunk heads are
# only 600 chars, so the *** START/END markers usually sit deeper in the
# chunk while the marker-less blurb ("The Project Gutenberg eBook ...",
# "This eBook is for the use of anyone ...") rides into notes.md verbatim.
# These case-insensitive hints match the standard PG header/footer blurb,
# never ordinary book prose.
_GUTENBERG_LINE_HINTS = (
    "project gutenberg",
    "gutenberg.org",
    "distributed proofreading",
    "pgdp.net",
    "this ebook is for the use of anyone",
    "at no cost and with almost no restrictions",
    "you may copy it, give it away or re-use it",
    "check the laws of the country",
    "before using this ebook",
    "most people start at our website",
)


def strip_gutenberg_boilerplate(text: str) -> tuple[str, bool]:
    """Drop PG blurb lines no marker strip can see; plain prose untouched."""
    # Fast path: one C-level scan skips splitlines + per-line lowers when no
    # hint is present (plain books); same (text, False) as the loop below.
    if not any(h in text.lower() for h in _GUTENBERG_LINE_HINTS):
        return text, False
    lines = text.splitlines()
    kept: list[str] = []
    for ln in lines:
        ll = ln.lower()
        if not any(h in ll for h in _GUTENBERG_LINE_HINTS):
            kept.append(ln)
    if len(kept) == len(lines):
        return text, False
    return "\n".join(kept), True


# Canonical PG license-tail openers (K-48 slice 3). The *** END marker often
# sits past a chunk head (freud 0254.txt line 83) or in an earlier chunk, so
# the tail chunks (0255-0258, which open mid-sentence on license prose) carry
# no marker at all. These exact tail phrases are never ordinary book prose.
_LICENSE_TAIL_HINTS = (
    "START: FULL LICENSE",
    "FULL PROJECT GUTENBERG",
)

# Mirrors extract._START_SCAN_LINES: a START marker only counts as a header
# when it sits in the chunk's first 600 lines.
_HEAD_SCAN_LINES = 600


def _clean_chunk(full: str) -> tuple[str | None, bool, bool]:
    """PG header/footer cuts on one chunk's full text (K-48 slice 3).

    Returns (source, cut, tail): source feeds the 600-char head, or None
    when the chunk is pure PG tail (skip it); cut reports a cut fired; tail
    tells the caller later chunks are tail too (the PG license always closes
    the file). Untouched chunks come back as the original string, so
    marker-free notes stay byte-identical.
    """
    # Fast path: plain chunks carry neither marker family, so the per-line
    # scans below cannot cut; skip splitlines + substring loops (same output).
    if "GUTENBERG" not in full and "FULL LICENSE" not in full:
        return full, False, False
    lines = full.splitlines()
    cut = False
    for i, line in enumerate(lines[:_HEAD_SCAN_LINES]):
        if any(m in line for m in TEXT_START_MARKERS):
            lines = lines[i + 1 :]
            cut = True
            break
    for j, line in enumerate(lines):
        if any(m in line for m in TEXT_END_MARKERS):
            return "\n".join(lines[:j]), True, True
    if any(h in full for h in _LICENSE_TAIL_HINTS):
        return None, True, True
    if not cut:
        return full, False, False
    return "\n".join(lines), True, False


# Steal: fenced-only behavior check, ported fresh from DietrichGebert/ponytail@7efd0b7c
# (MIT, https://github.com/DietrichGebert/ponytail/pull/966) benchmarks/behavior.js:
# onecheck scans only inside fenced blocks, then strips strings/comments
# before the assert/test regex. No donor code copied; stdlib-only Python port.
_BT = chr(96)
_DQ = chr(34)
_SQ = chr(39)
_FENCE_RE = re.compile(_BT * 3 + r"[^\n]*\n?([\s\S]*?)" + _BT * 3)
_CHECK_RE = re.compile(r"\b(assert|expect|test|it|describe)\b")
_TRIPLE_DQ_RE = re.compile(_DQ * 3 + r"[\s\S]*?" + _DQ * 3)
_TRIPLE_SQ_RE = re.compile(_SQ * 3 + r"[\s\S]*?" + _SQ * 3)
_DQ_RE = re.compile(_DQ + r"(?:\\.|[^" + _DQ + r"\\\n])*" + _DQ)
_SQ_RE = re.compile(_SQ + r"(?:\\.|[^" + _SQ + r"\\\n])*" + _SQ)
_TICK_RE = re.compile(_BT + r"(?:\\.|[^" + _BT + r"\\])*" + _BT)
_BLOCK_COMMENT_RE = re.compile(r"/\*[\s\S]*?\*/")
_LINE_COMMENT_RE = re.compile(r"(?://[^\n]*|#[^\n]*)")


def fenced_blocks(text):
    # Code inside fenced blocks (info line dropped); prose outside ignored.
    return [m.group(1) for m in _FENCE_RE.finditer(text)]


def strip_strings_comments(code):
    # Blank strings/comments so the assert/test regex sees runnable code only.
    for rx in (_TRIPLE_DQ_RE, _TRIPLE_SQ_RE, _DQ_RE, _SQ_RE, _TICK_RE):
        code = rx.sub(_DQ * 2, code)
    code = _BLOCK_COMMENT_RE.sub("", code)
    return "\n".join(_LINE_COMMENT_RE.sub("", ln) for ln in code.splitlines())


def grade_fenced(text):
    # True when cleaned fenced code holds a check; prose alone never passes.
    for block in fenced_blocks(text):
        if _CHECK_RE.search(strip_strings_comments(block)):
            return True
    return False


# Steal: scope router + disclaimer lane, ported fresh from pras-ops/indian-business-ops-skills
# (MIT, https://github.com/pras-ops/indian-business-ops-skills/blob/main/skills/gst-compliance/SKILL.md
# plus DISCLAIMER.md): a NOT-for line keeps the skill in its lane, a verify-before-act
# footer sends regulated steps back to the source. No donor text copied.
# Steal: thin-router scaffold shape, ported fresh from mattpocock/skills@b0618bc
# (MIT, https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/engineering/implement/SKILL.md):
# frontmatter carries the trigger, the body only routes to sibling refs plus peer
# Skill-call composition lines. No donor text copied.
def _scaffold_body(name: str) -> str:
    return (
        f"\n# {name}\n\nBuilt from owned sources. "
        "Start with `chapters/notes.md`, then `glossary.md`, "
        "`patterns.md`, `cheatsheet.md`. Use when the trigger "
        "topic matches this skill description.\n"
        "NOT for: topics outside this skill (leave them to the skill that owns them).\n"
        "Routes - read only the sibling that matches the task:\n"
        "- Terms: see `glossary.md`.\n"
        "- Patterns: see `patterns.md`.\n"
        "- Recall: see `cheatsheet.md`.\n"
        "Compose with peers when the task spans skills:\n"
        "- For the peer-owned step, call it via `Skill: peer-skill-name`.\n"
        "- After this skill route, call the next skill via `Skill: peer-skill-name`.\n"
        "Verify before acting: check the source before any regulated, filed, or paid step.\n"
    )


def scaffold_leftovers(skilldir: Path) -> list[str]:
    """Files of the skill that still hold the scaffold's placeholder text (SKILL.md body, glossary, patterns, cheatsheet)."""
    left = []
    try:
        text = (skilldir / "SKILL.md").read_text(encoding="utf-8")
    except OSError:
        return ["SKILL.md"]
    body = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", text, count=1, flags=re.S)
    if body.replace("\r\n", "\n").strip() == _scaffold_body(skilldir.name).strip():
        left.append("SKILL.md")
    for fname, stub in STUB_FILES.items():
        try:
            if (skilldir / fname).read_text(encoding="utf-8").replace("\r\n", "\n").strip() == stub.strip():
                left.append(fname)
        except OSError:
            continue
    return left


def prompt_version() -> str:
    """Version stamp of the chapter-to-skill prompt fragment (llm pattern)."""
    try:
        text = PROMPT_FILE.read_text(encoding="utf-8")
    except OSError:
        return "inline"
    m = re.search(r"^version:\s*(\S+)", text, re.M)
    return m.group(1) if m else "unversioned"


def _frontmatter(name: str, description: str, version: str = "0.1.0",
                  author: str = "skillworks", tags: list[str] | None = None,
                  licence: str = "MIT") -> str:
    safe = "".join(c if c.isalnum() or c == "-" else "-" for c in name.lower()).strip("-")
    tag_list = tags if tags is not None else []
    tags_str = "[" + ", ".join(tag_list) + "]"
    return (
        f"---\nname: {safe}\ndescription: {description}\n"
        f"version: {version}\nauthor: {author}\ntags: {tags_str}\nlicense: {licence}\n---\n"
    )


def build(workdir: Path, skilldir: Path, name: str, description: str) -> dict:
    validate_name(name, skilldir)
    heads = []
    pg_cut = False
    tailed = False
    chunk_paths = sorted((workdir / "chunks").glob("*.txt"))
    for path in chunk_paths:
        if tailed:
            pg_cut = True
            continue
        full = path.read_text(encoding="utf-8")
        source, cut, tail = _clean_chunk(full)
        if cut:
            pg_cut = True
        if tail:
            tailed = True
            if source is None:
                continue
        if source is None:
            continue
        heads.append(f"## {path.stem}\n" + source[:600])
    chapters = skilldir / "chapters"
    chapters.mkdir(parents=True, exist_ok=True)
    notes, marked = strip_gutenberg_markers("\n\n".join(heads))
    notes, blurbed = strip_gutenberg_boilerplate(notes)
    (chapters / "notes.md").write_text(notes, encoding="utf-8")
    noncommercial = is_noncommercial_text(description)
    licence = NC_LICENSE if noncommercial else "MIT"
    (skilldir / "SKILL.md").write_text(_frontmatter(name, description, licence=licence) + _scaffold_body(name), encoding="utf-8")
    for fname, stub in STUB_FILES.items():
        (skilldir / fname).write_text(stub, encoding="utf-8")
    refs = skilldir / "references"
    refs.mkdir(exist_ok=True)
    chunks = chunk_paths
    sources_note = (
        "\nLicence: CC BY-NC-SA 3.0 (source) — NonCommercial, never sold; "
        "share free under the same licence.\n"
        if noncommercial else ""
    )
    (refs / "sources.md").write_text(
        "# Sources\n\nProgressive disclosure: read SKILL.md first, then only "
        "the chunk listed here that matches the task.\n"
        + sources_note
        + "".join(f"- `{p.name}`\n" for p in chunks),
        encoding="utf-8",
    )
    receipt = {
        "stage": "build",
        "skill": str(skilldir),
        "note_chars": len(notes),
        "notes_stripped": bool(marked or blurbed or pg_cut),
        "noncommercial": noncommercial,
        "prompt": prompt_version(),
        "layout": "skill-pack",
    }
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt
