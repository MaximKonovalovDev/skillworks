"""Build stage: two-pass notes-then-skill scaffold.

Pass 1 condenses chunk heads into notes. Pass 2 writes the skill scaffold:
SKILL.md with spec frontmatter plus chapters, glossary, patterns, cheatsheet.
An LLM pass can enrich notes later; the scaffold is always valid alone.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "build-skill.md"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_RULE = "name matches dir, a-z0-9- only"


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


def _scaffold_body(name: str) -> str:
    return (
        f"\n# {name}\n\nBuilt from owned sources. "
        "Start with `chapters/notes.md`, then `glossary.md`, "
        "`patterns.md`, `cheatsheet.md`. Use when the trigger "
        "topic matches this skill description.\n"
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
                 author: str = "skillworks", tags: list[str] | None = None) -> str:
    safe = "".join(c if c.isalnum() or c == "-" else "-" for c in name.lower()).strip("-")
    tag_list = tags if tags is not None else []
    tags_str = "[" + ", ".join(tag_list) + "]"
    return (
        f"---\nname: {safe}\ndescription: {description}\n"
        f"version: {version}\nauthor: {author}\ntags: {tags_str}\nlicense: MIT\n---\n"
    )


def build(workdir: Path, skilldir: Path, name: str, description: str) -> dict:
    validate_name(name, skilldir)
    heads = []
    for path in sorted((workdir / "chunks").glob("*.txt")):
        heads.append(f"## {path.stem}\n" + path.read_text(encoding="utf-8")[:600])
    chapters = skilldir / "chapters"
    chapters.mkdir(parents=True, exist_ok=True)
    notes = "\n\n".join(heads)
    (chapters / "notes.md").write_text(notes, encoding="utf-8")
    (skilldir / "SKILL.md").write_text(_frontmatter(name, description) + _scaffold_body(name), encoding="utf-8")
    for fname, stub in STUB_FILES.items():
        (skilldir / fname).write_text(stub, encoding="utf-8")
    refs = skilldir / "references"
    refs.mkdir(exist_ok=True)
    chunks = sorted((workdir / "chunks").glob("*.txt"))
    (refs / "sources.md").write_text(
        "# Sources\n\nProgressive disclosure: read SKILL.md first, then only "
        "the chunk listed here that matches the task.\n\n"
        + "".join(f"- `{p.name}`\n" for p in chunks),
        encoding="utf-8",
    )
    receipt = {
        "stage": "build",
        "skill": str(skilldir),
        "note_chars": len(notes),
        "prompt": prompt_version(),
        "layout": "skill-pack",
    }
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt
