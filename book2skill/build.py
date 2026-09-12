"""Build stage: two-pass notes-then-skill scaffold.

Pass 1 condenses chunk heads into notes. Pass 2 writes the skill scaffold:
SKILL.md with spec frontmatter plus chapters, glossary, patterns, cheatsheet.
An LLM pass can enrich notes later; the scaffold is always valid alone.
"""
from __future__ import annotations

import json
from pathlib import Path


def _frontmatter(name: str, description: str) -> str:
    safe = "".join(c if c.isalnum() or c == "-" else "-" for c in name.lower()).strip("-")
    return f"---\nname: {safe}\ndescription: {description}\nlicense: MIT\n---\n"


def build(workdir: Path, skilldir: Path, name: str, description: str) -> dict:
    heads = []
    for path in sorted((workdir / "chunks").glob("*.txt")):
        heads.append(f"## {path.stem}\n" + path.read_text(encoding="utf-8")[:600])
    chapters = skilldir / "chapters"
    chapters.mkdir(parents=True, exist_ok=True)
    notes = "\n\n".join(heads)
    (chapters / "notes.md").write_text(notes, encoding="utf-8")
    (skilldir / "SKILL.md").write_text(
        _frontmatter(name, description)
        + (
            f"\n# {name}\n\nBuilt from owned sources. "
            "Start with `chapters/notes.md`, then `glossary.md`, "
            "`patterns.md`, `cheatsheet.md`. Use when the trigger "
            "topic matches this skill description.\n"
        ),
        encoding="utf-8",
    )
    (skilldir / "glossary.md").write_text("# Glossary\n\nFill terms while reading.\n", encoding="utf-8")
    (skilldir / "patterns.md").write_text("# Patterns\n\nFill reusable patterns while reading.\n", encoding="utf-8")
    (skilldir / "cheatsheet.md").write_text("# Cheatsheet\n\nFill one-page recall while reading.\n", encoding="utf-8")
    (skilldir / "references").mkdir(exist_ok=True)
    receipt = {"stage": "build", "skill": str(skilldir), "note_chars": len(notes)}
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt
