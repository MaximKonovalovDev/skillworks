"""K-48: build strips the Gutenberg header/footer at build time.

Stale chunks (split before extract learned to strip) still carry the PG
boilerplate, and build used to copy chunk heads verbatim into
chapters/notes.md, so freud's notes still open with the PG eBook blurb.
Build must clean heads: *** markers via the extract strip plus the
marker-less blurb lines (the real stale heads carry no *** markers).
"""
from pathlib import Path

from book2skill import build as build_mod

HEADER_BLURB = (
    "The Project Gutenberg eBook of Test Dreams\n"
    "    \n"
    "This eBook is for the use of anyone anywhere in the United States and\n"
    "most other parts of the world at no cost and with almost no restrictions\n"
    "whatsoever. You may copy it, give it away or re-use it under the terms\n"
    "of the Project Gutenberg License included with this eBook or online\n"
    "at www.gutenberg.org. If you are not located in the United States,\n"
    "you will have to check the laws of the country where you are located\n"
    "before using this eBook.\n"
    "\n"
    "Title: Test Dreams\n"
    "\n"
    "Author: Test Author\n"
)

FOOTER_BLURB = (
    "*** END OF THE PROJECT GUTENBERG EBOOK TEST DREAMS ***\n"
    "Most people start at our website\n"
)


def _work_with_stale_chunks(work: Path) -> None:
    chunks = work / "chunks"
    chunks.mkdir(parents=True)
    (chunks / "0000.txt").write_text(
        HEADER_BLURB + "Dream analysis chapter zero about free association.\n" * 40,
        encoding="utf-8",
    )
    (chunks / "0001.txt").write_text(
        "Dream analysis chapter one about condensation.\n" * 40,
        encoding="utf-8",
    )
    (chunks / "0002.txt").write_text(
        "Dream analysis chapter two about displacement.\n" * 10 + FOOTER_BLURB,
        encoding="utf-8",
    )


def test_build_strips_gutenberg_header_and_footer(tmp_path: Path) -> None:
    work = tmp_path / "work"
    _work_with_stale_chunks(work)
    skill = tmp_path / "skill"
    receipt = build_mod.build(work, skill, "skill", "demo description")
    notes = (skill / "chapters" / "notes.md").read_text(encoding="utf-8")
    assert "Gutenberg" not in notes and "gutenberg" not in notes
    assert "*** START OF" not in notes and "*** END OF" not in notes
    assert "Most people start at our website" not in notes
    assert "This eBook is for the use of anyone" not in notes
    assert "free association" in notes  # body kept
    assert "condensation" in notes
    assert "## 0000" in notes  # section structure kept
    assert receipt["notes_stripped"] is True


def test_build_leaves_plain_chunks_untouched(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about leases", encoding="utf-8")
    skill = tmp_path / "skill"
    receipt = build_mod.build(work, skill, "skill", "demo description")
    notes = (skill / "chapters" / "notes.md").read_text(encoding="utf-8")
    assert "chapter about leases" in notes
    assert receipt["notes_stripped"] is False
