"""K-53 R5: one build, four copy-layout exports (claude/codex/opencode/gemini).

Same code path, no target forks beyond the layout root: each target yields an
importable layout with SKILL.md at the root plus a per-target ZIP (K-41 shape),
a .lock.json naming the target, the eval gate and the scaffold hold for every
target, and the nesting guard (export/ left out, links never followed).
"""
import json
import zipfile
from pathlib import Path

import pytest

from book2skill import build as build_mod
from book2skill import export as export_mod

REPORT = {"rate": 1.0, "total": 1, "passed": 1}
LOW_REPORT = {"rate": 0.5, "total": 2, "passed": 1}


def _skill(root: Path, name: str = "demo-skill") -> Path:
    skill = root / name
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Use when testing export targets.\n---\nWritten body.\n",
        encoding="utf-8",
    )
    (skill / "references" / "a.md").write_text("reference a\n", encoding="utf-8")
    return skill


def test_layouts_cover_all_targets() -> None:
    """One layout descriptor per target, each rooted at SKILL.md (fails before K-53)."""
    assert set(export_mod.LAYOUTS) == set(export_mod.TARGETS) == {"claude", "codex", "opencode", "gemini"}
    for target in export_mod.TARGETS:
        layout = export_mod.layout_for(target)
        assert layout["root_file"] == "SKILL.md"
    with pytest.raises(Exception):
        export_mod.layout_for("not-a-target")


@pytest.mark.parametrize("target", export_mod.TARGETS)
def test_target_yields_importable_layout(tmp_path: Path, target: str) -> None:
    """Each target: dest has SKILL.md at the root; ZIP has SKILL.md at the root."""
    skill = _skill(tmp_path)
    dist = tmp_path / "dist"
    receipt = export_mod.export(skill, target, dist, eval_report=REPORT)
    dest = Path(receipt["dest"])
    assert dest == dist / target / skill.name
    assert (dest / "SKILL.md").read_bytes() == (skill / "SKILL.md").read_bytes()
    assert (dest / ".lock.json").is_file()
    lock = json.loads((dest / ".lock.json").read_text(encoding="utf-8"))
    assert lock["target"] == target
    zip_path = Path(receipt["zip"])
    assert zip_path == dist / target / f"{skill.name}.zip"
    with zipfile.ZipFile(zip_path) as bundle:
        names = bundle.namelist()
        assert "SKILL.md" in names
        assert not any(n.startswith(f"{skill.name}/") for n in names)
        assert bundle.read("SKILL.md") == (skill / "SKILL.md").read_bytes()


@pytest.mark.parametrize("target", export_mod.TARGETS)
def test_gate_refused_for_every_target(tmp_path: Path, target: str) -> None:
    skill = _skill(tmp_path)
    dist = tmp_path / "dist"
    with pytest.raises(SystemExit) as exc:
        export_mod.export(skill, target, dist, eval_report=LOW_REPORT)
    assert "refused" in str(exc.value)
    assert not (dist / target / skill.name).exists()
    assert not (dist / target / f"{skill.name}.zip").exists()


@pytest.mark.parametrize("target", export_mod.TARGETS)
def test_scaffold_held_for_every_target(tmp_path: Path, target: str) -> None:
    """A pure-scaffold skill is held on every target; once written it ships."""
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about leases", encoding="utf-8")
    skill = tmp_path / "skills" / "demo-skill"
    build_mod.build(work, skill, "demo-skill", "Use when handling leases.")
    assert build_mod.scaffold_leftovers(skill) != []
    (skill / "eval_report.json").write_text(
        json.dumps({"rate": 1.0, "total": 3, "passed": 3}), encoding="utf-8")
    out = tmp_path / "dist"
    with pytest.raises(SystemExit) as exc:
        export_mod.export(skill, target, out)
    assert "still hold the scaffold text" in str(exc.value)
    assert not (out / target / skill.name).exists()
