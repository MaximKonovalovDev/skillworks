"""Export nesting guard (2026-10-03: nested export paths of 200-5000 characters crashed the OpenCode server 9 times).

K-07 covered one case: --out inside the skill dir under a top folder. This file covers the class:
every target, every place --out can sit, a stale export/ folder left in the skill, a source that is
also the destination, links that loop, and paths past the Windows limit.
"""
import os
import shutil
from pathlib import Path

import pytest

from book2skill import export as export_mod

REPORT = {"rate": 1.0, "total": 1, "passed": 1}
LIMIT = export_mod.MAX_DEST_PATH


def _skill(root: Path, name: str = "demo-skill") -> Path:
    skill = root / name
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(f"---\nname: {name}\ndescription: demo\n---\nbody\n", encoding="utf-8")
    (skill / "references" / "a.md").write_text("reference a\n", encoding="utf-8")
    return skill


def _no_nesting(dest: Path, skill: Path) -> None:
    assert (dest / "SKILL.md").exists()
    assert (dest / "references" / "a.md").exists()
    for bad in ("export", "claude", "codex", "opencode", "gemini", skill.name):
        assert not (dest / bad).exists(), f"{dest / bad} is a nested copy"
    assert max(len(str(p)) for p in dest.rglob("*")) < LIMIT


@pytest.mark.parametrize("target", export_mod.TARGETS)
@pytest.mark.parametrize("where", ["export", "export/deep/er", "plain-out", ".", "dist-in-skill"])
def test_out_inside_skill_every_target(tmp_path: Path, target: str, where: str) -> None:
    """--out anywhere inside the skill dir, including the skill dir itself, never copies itself into itself."""
    skill = _skill(tmp_path)
    out = skill if where == "." else skill / where
    # run every target twice so a second export sees the first one's output
    for t in export_mod.TARGETS:
        export_mod.export(skill, t, out, eval_report=REPORT)
    export_mod.export(skill, target, out, eval_report=REPORT)
    _no_nesting(out / target / skill.name, skill)


@pytest.mark.parametrize("target", export_mod.TARGETS)
def test_stale_export_folder_is_not_shipped(tmp_path: Path, target: str) -> None:
    """A skill dir that still holds an old export/ tree (git-ignored, left by the earlier bug) ships without it."""
    skill = _skill(tmp_path)
    stale = skill / "export" / "claude" / skill.name / "export" / "claude" / skill.name
    stale.mkdir(parents=True)
    (stale / "SKILL.md").write_text("stale copy\n", encoding="utf-8")
    dist = tmp_path / "dist"
    export_mod.export(skill, target, dist, eval_report=REPORT)
    _no_nesting(dist / target / skill.name, skill)


def test_source_that_is_the_destination_is_refused_and_kept(tmp_path: Path) -> None:
    """Exporting dist/claude/<name> into dist would delete its own source: refuse, keep the files."""
    dist = tmp_path / "dist"
    skill = _skill(dist / "claude")
    with pytest.raises(SystemExit) as exc:
        export_mod.export(skill, "claude", dist, eval_report=REPORT)
    assert "export refused" in str(exc.value)
    assert (skill / "SKILL.md").exists() and (skill / "references" / "a.md").exists()


def test_destination_above_the_source_is_refused(tmp_path: Path) -> None:
    """dest = out/target/name must never sit above the skill dir (rmtree would take the source with it)."""
    out = tmp_path / "out"
    skill = _skill(out / "claude" / "demo-skill" / "sub")  # out/claude/demo-skill/sub/demo-skill
    with pytest.raises(SystemExit) as exc:
        export_mod.export(skill, "claude", out, eval_report=REPORT)
    assert "export refused" in str(exc.value)
    assert (skill / "SKILL.md").exists()


def _link_dir(link: Path, target: Path) -> bool:
    """A directory link that loops back (symlink, else a Windows junction). False when the PC allows neither."""
    try:
        os.symlink(target, link, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        pass
    try:
        import _winapi  # type: ignore[import-not-found]

        _winapi.CreateJunction(str(target), str(link))
        return True
    except (ImportError, OSError, AttributeError):
        return False


def test_looping_link_is_not_followed(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    if not _link_dir(skill / "loop", skill):
        pytest.skip("this PC allows neither symlinks nor junctions")
    dist = tmp_path / "dist"
    export_mod.export(skill, "claude", dist, eval_report=REPORT)
    dest = dist / "claude" / skill.name
    assert (dest / "SKILL.md").exists()
    assert not (dest / "loop").exists()
    assert max(len(str(p)) for p in dest.rglob("*")) < LIMIT
    shutil.rmtree(skill / "loop", ignore_errors=True)


def test_path_past_the_limit_is_refused_before_any_copy(tmp_path: Path) -> None:
    """A tree whose exported paths pass the limit stops with a clear message instead of crashing a file watcher."""
    skill = _skill(tmp_path)
    deep = skill / "references"
    for _ in range(30):
        deep = deep / "section-with-a-long-name"
    deep.mkdir(parents=True)
    (deep / "x.md").write_text("deep\n", encoding="utf-8")
    dist = tmp_path / "dist"
    with pytest.raises(SystemExit) as exc:
        export_mod.export(skill, "claude", dist, eval_report=REPORT)
    assert "export refused" in str(exc.value) and "characters" in str(exc.value)
    assert not (dist / "claude" / skill.name).exists()


def test_normal_export_still_copies_everything(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    dist = tmp_path / "dist"
    for target in export_mod.TARGETS:
        receipt = export_mod.export(skill, target, dist, eval_report=REPORT)
        dest = Path(receipt["dest"])
        assert (dest / "SKILL.md").read_text(encoding="utf-8") == (skill / "SKILL.md").read_text(encoding="utf-8")
        assert (dest / "references" / "a.md").exists()
        assert (dest / ".lock.json").exists()
