"""Steal thin-router: built scaffold routes to sibling refs plus peer Skill calls, SKILL.md under 40 lines."""
from pathlib import Path

from book2skill import build as build_mod


def _built_text(tmp_path: Path) -> str:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about routing", encoding="utf-8")
    skill = tmp_path / "skills" / "demo-router"
    build_mod.build(work, skill, "demo-router", "Use when routing tasks.")
    return (skill / "SKILL.md").read_text(encoding="utf-8")


def test_router_has_three_sibling_refs(tmp_path: Path) -> None:
    text = _built_text(tmp_path)
    assert "Routes - read only the sibling that matches the task:" in text
    assert text.count("`glossary.md`") >= 1
    assert text.count("`patterns.md`") >= 1
    assert text.count("`cheatsheet.md`") >= 1
    assert "Built from owned sources. Start with `chapters/notes.md`" in text


def test_router_has_two_peer_skill_calls(tmp_path: Path) -> None:
    text = _built_text(tmp_path)
    assert "Compose with peers when the task spans skills:" in text
    assert text.count("Skill: peer-skill-name") >= 2


def test_router_skill_md_under_40_lines(tmp_path: Path) -> None:
    text = _built_text(tmp_path)
    assert len(text.splitlines()) <= 40
    assert "NOT for:" in text
    assert "Verify before acting:" in text
