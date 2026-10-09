"""Build speed slice: output identical after fast-path + single glob.

Pins that the speedup keeps bytes identical: plain chunks pass through
untouched, PG header/footer still stripped, sources.md still lists chunks.
"""
from pathlib import Path

from book2skill import build as build_mod


def test_speed_plain_notes_byte_identical(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about leases\n", encoding="utf-8")
    skill = tmp_path / "skill"
    receipt = build_mod.build(work, skill, "skill", "demo description")
    notes = (skill / "chapters" / "notes.md").read_text(encoding="utf-8")
    assert notes == "## 0000\nchapter about leases\n"
    assert receipt["notes_stripped"] is False
    sources = (skill / "references" / "sources.md").read_text(encoding="utf-8")
    assert "- `0000.txt`" in sources


def test_speed_gutenberg_still_stripped(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    header = (
        "The Project Gutenberg eBook of Test Dreams\n"
        "This eBook is for the use of anyone anywhere in the United States\n"
        "*** START OF THE PROJECT GUTENBERG EBOOK TEST DREAMS ***\n"
    )
    (work / "chunks" / "0000.txt").write_text(
        header + "Dream analysis chapter zero.\n" * 20, encoding="utf-8"
    )
    (work / "chunks" / "0001.txt").write_text(
        "Dream analysis chapter one.\n" * 20, encoding="utf-8"
    )
    skill = tmp_path / "skill"
    receipt = build_mod.build(work, skill, "skill", "demo description")
    notes = (skill / "chapters" / "notes.md").read_text(encoding="utf-8")
    assert "Gutenberg" not in notes and "gutenberg" not in notes
    assert "chapter zero" in notes and "chapter one" in notes
    assert receipt["notes_stripped"] is True


def test_speed_clean_chunk_fast_path_matches(tmp_path: Path) -> None:
    plain = "plain prose about leases with no markers\n" * 10
    assert build_mod._clean_chunk(plain) == (plain, False, False)
    marked = "*** START OF THE PROJECT GUTENBERG EBOOK X ***\nbody here\n"
    src, cut, tail = build_mod._clean_chunk(marked)
    assert cut is True and "body here" in src
