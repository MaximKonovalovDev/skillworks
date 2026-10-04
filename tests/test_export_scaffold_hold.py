"""pilot-105: no ship path hands a stranger placeholder text.

A pure-scaffold skill (fresh `build`, placeholder SKILL.md + glossary +
patterns + cheatsheet) is refused on the direct `export` path with the file
names, the same hold `make --target` already prints. Once an author writes
the files, the same direct path ships.
"""
import json
import zipfile
from pathlib import Path

from click.testing import CliRunner

from book2skill import build as build_mod
from book2skill.cli import main

PLACEHOLDERS = ["SKILL.md", "glossary.md", "patterns.md", "cheatsheet.md"]


def test_direct_export_holds_a_pure_scaffold_and_ships_once_written(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about leases", encoding="utf-8")
    skill = tmp_path / "skills" / "demo-skill"
    build_mod.build(work, skill, "demo-skill", "Use when handling leases.")
    assert build_mod.scaffold_leftovers(skill) == PLACEHOLDERS
    (skill / "eval_report.json").write_text(
        json.dumps({"rate": 1.0, "total": 3, "passed": 3}), encoding="utf-8")
    out = tmp_path / "dist"

    held = CliRunner().invoke(
        main, ["export", "--skill", str(skill), "--target", "claude", "--out", str(out)])
    assert held.exit_code == 1, held.output
    for name in PLACEHOLDERS:
        assert name in held.output, held.output
    assert "export held" in held.output and "still hold the scaffold text" in held.output
    assert not out.exists(), "a held export writes no bundle"

    (skill / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Use when handling leases.\n---\nRenew a lease in writing.\n",
        encoding="utf-8")
    for fname in ("glossary.md", "patterns.md", "cheatsheet.md"):
        (skill / fname).write_text(f"# {fname}\n\nwritten by hand\n", encoding="utf-8")
    assert build_mod.scaffold_leftovers(skill) == []

    shipped = CliRunner().invoke(
        main, ["export", "--skill", str(skill), "--target", "claude", "--out", str(out)])
    assert shipped.exit_code == 0, shipped.output
    assert (out / "claude" / "demo-skill" / "SKILL.md").is_file()
    with zipfile.ZipFile(out / "claude" / "demo-skill.zip") as bundle:
        assert "SKILL.md" in bundle.namelist()
