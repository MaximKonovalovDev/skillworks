"""BK-1005-1: chapter-aware split plus fixed skill shape.

F2P: split emits chapters files matching headings on the progit sample.
P2P: python -m pytest tests/ -q green plus node sprint/check.mjs PASS.
Sources stay in work/ (git-ignored); this file only reads them.
"""
from pathlib import Path

import pytest

from book2skill import audit as audit_mod
from book2skill import gates as gates_mod
from book2skill import split_chapters as sc_mod

ROOT = Path(__file__).resolve().parent.parent
PROGIT = ROOT / "work" / "progit-branching" / "full_text.txt"

DESC = "Pro Git branching demo. Use when a loop must branch or merge."


def _work_with_text(tmp_path: Path, text: str) -> Path:
    work = tmp_path / "work"
    work.mkdir(parents=True)
    (work / "full_text.txt").write_text(text, encoding="utf-8")
    return work


def test_split_emits_chapters_matching_progit_headings(tmp_path: Path) -> None:
    if not PROGIT.is_file():
        pytest.skip("work/progit-branching sample not present")
    work = tmp_path / "work"
    work.mkdir()
    (work / "full_text.txt").write_text(PROGIT.read_text(encoding="utf-8"), encoding="utf-8")
    skill = tmp_path / "progit-branching"
    receipt = sc_mod.split_chapters(work, skill, "progit-branching", DESC)
    files = sorted((skill / "chapters").glob("*.md"))
    assert receipt["chapters"] == len(files) > 5
    assert receipt["distinct"] == len(files)
    titles = [sc_mod.detect_chapters(PROGIT.read_text(encoding="utf-8"))[i]["title"] for i in range(len(files))]
    assert "Git Branching" in titles
    assert "Basic Branching and Merging" in titles
    assert "Branch Management" in titles
    assert "Rebasing" in titles
    assert all(len(t) <= sc_mod.TITLE_CAP for t in titles)
    names = " ".join(p.name for p in files)
    for junk in ("on-branch-master", "it-looks-like", "changes-to-be-committed",
                 "merge-head", "modified-index-html", "all-conflicts"):
        assert junk not in names


def test_progit_chapters_keep_fixed_shape_and_budgets(tmp_path: Path) -> None:
    if not PROGIT.is_file():
        pytest.skip("work/progit-branching sample not present")
    work = tmp_path / "work"
    work.mkdir()
    (work / "full_text.txt").write_text(PROGIT.read_text(encoding="utf-8"), encoding="utf-8")
    skill = tmp_path / "progit-branching"
    sc_mod.split_chapters(work, skill, "progit-branching", DESC)
    for rel in ("SKILL.md", "glossary.md", "patterns.md", "cheatsheet.md"):
        assert (skill / rel).is_file(), rel
    report = audit_mod.audit(skill)
    assert report["total_tokens"] <= gates_mod.TOTAL_TOKEN_BUDGET
    assert report["body_tokens"] <= gates_mod.BODY_TOKEN_BUDGET


def test_headings_inside_fenced_blocks_are_not_chapters() -> None:
    text = "== Real\n\nbody\n\n----\n== Fake\n# Also fake\n----\n\n== Next\n\nmore\n"
    rows = sc_mod.detect_chapters(text)
    assert [r["title"] for r in rows] == ["Real", "Next"]


def test_markdown_headings_split_too(tmp_path: Path) -> None:
    work = _work_with_text(tmp_path, "# Alpha\n\naa\n\n## Beta\n\nbb\n")
    skill = tmp_path / "demo-book"
    receipt = sc_mod.split_chapters(work, skill, "demo-book", DESC)
    assert receipt["chapters"] == 2
    assert (skill / "chapters" / "01-alpha.md").is_file()
    assert (skill / "chapters" / "02-beta.md").is_file()
    assert "bb" in (skill / "chapters" / "02-beta.md").read_text(encoding="utf-8")


def test_duplicate_titles_get_distinct_slugs() -> None:
    rows = sc_mod.detect_chapters("== Same\n\na\n\n== Same\n\nb\n")
    assert [r["slug"] for r in rows] == ["same", "same-2"]


def test_long_titles_cap_at_80_chars() -> None:
    rows = sc_mod.detect_chapters("== " + "w" * 120 + "\n\nbody\n")
    assert len(rows[0]["title"]) <= sc_mod.TITLE_CAP == 80


def test_text_without_headings_becomes_one_notes_chapter(tmp_path: Path) -> None:
    work = _work_with_text(tmp_path, "plain prose with no headings at all\n")
    skill = tmp_path / "plain-book"
    receipt = sc_mod.split_chapters(work, skill, "plain-book", DESC)
    assert receipt["chapters"] == 1 == receipt["distinct"]
    files = list((skill / "chapters").glob("*.md"))
    assert len(files) == 1 and "no headings" in files[0].read_text(encoding="utf-8")
