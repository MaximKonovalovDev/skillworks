"""Steal scope-router: built scaffold carries a NOT-for scope line and a verify-before-act footer."""
from pathlib import Path

from book2skill import build as build_mod


def test_scaffold_has_not_for_scope_line(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about leases", encoding="utf-8")
    skill = tmp_path / "skills" / "demo-skill"
    build_mod.build(work, skill, "demo-skill", "Use when handling leases.")
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert "NOT for:" in text


def test_scaffold_has_verify_before_act_disclaimer(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about leases", encoding="utf-8")
    skill = tmp_path / "skills" / "demo-skill"
    build_mod.build(work, skill, "demo-skill", "Use when handling leases.")
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert "Verify before acting:" in text
    assert "SKILL.md" in build_mod.scaffold_leftovers(skill)
