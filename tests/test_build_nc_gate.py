"""K-48 slice (1): a NonCommercial source can never get a price (build.py gate).

Today build.py writes `license: MIT` for every scaffold and nothing refuses a
price on an NC source (progit vol0 line 5 still says paid Vol 1 $10). After the
fix: build records the NC licence, and export refuses an NC skill that carries
a structured price (price.txt / pack.json / listing.md Price $N).
"""
from pathlib import Path

import pytest

from book2skill import build as build_mod
from book2skill import export as export_mod

REPORT = {"rate": 1.0, "total": 1, "passed": 1}

NC_DESC = "Pro Git branching (CC BY-NC-SA 3.0): branches and merges. Use when branching."


def _skill(root: Path, name: str, desc: str) -> Path:
    skill = root / name
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {desc}\nlicense: MIT\n---\nbody\n",
        encoding="utf-8",
    )
    (skill / "references" / "sources.md").write_text(
        "# Sources\n\nPro Git ch.3 (CC BY-NC-SA 3.0).\n", encoding="utf-8"
    )
    return skill


def test_build_records_nc_licence_instead_of_bare_mit(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about branching", encoding="utf-8")
    skill = tmp_path / "nc-skill"
    build_mod.build(work, skill, "nc-skill", NC_DESC)
    head = (skill / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
    assert "NonCommercial" in head and "never sold" in head
    assert "license: MIT" not in head


def test_export_refuses_nc_skill_with_price_txt(tmp_path: Path) -> None:
    skill = _skill(tmp_path, "nc-skill", NC_DESC)
    (skill / "price.txt").write_text("$10\n", encoding="utf-8")
    dist = tmp_path / "dist"
    with pytest.raises(SystemExit, match="NonCommercial"):
        export_mod.export(skill, "claude", dist, eval_report=REPORT)
    assert not (dist / "claude" / skill.name).exists()


def test_export_passes_nc_skill_without_price(tmp_path: Path) -> None:
    skill = _skill(tmp_path, "nc-skill", NC_DESC)
    receipt = export_mod.export(skill, "claude", tmp_path / "dist", eval_report=REPORT)
    assert Path(receipt["zip"]).is_file()


def test_export_passes_commercial_skill_with_price(tmp_path: Path) -> None:
    skill = _skill(tmp_path, "ok-skill", "Use when chaining commands in PowerShell.")
    (skill / "SKILL.md").write_text(
        "---\nname: ok-skill\ndescription: Use when chaining commands in PowerShell.\nlicense: MIT\n---\nbody\n",
        encoding="utf-8",
    )
    (skill / "references" / "sources.md").write_text("# Sources\n\nOwn notes.\n", encoding="utf-8")
    (skill / "price.txt").write_text("$10\n", encoding="utf-8")
    receipt = export_mod.export(skill, "claude", tmp_path / "dist", eval_report=REPORT)
    assert Path(receipt["zip"]).is_file()
