"""K-18 [S01-C4]: rebuilt seed frontmatter carries version/author/tags, name+description first."""
from pathlib import Path

from book2skill import build as build_mod


def test_rebuilt_seed_frontmatter_versioned(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about branching", encoding="utf-8")
    skill = tmp_path / "progit-branching"
    build_mod.build(work, skill, "progit-branching", "Pro Git branching demo")
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---")
    head = text.split("---")[1]
    assert "name: progit-branching" in head and "description:" in head
    assert "version: 0.1.0" in head and "author:" in head and "tags:" in head
    assert head.index("name:") < head.index("description:") < head.index("version:")
    assert head.index("version:") < head.index("author:") < head.index("tags:")
