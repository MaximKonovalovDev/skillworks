"""K-48 slice (3): build strips the PG header/footer at build time, fully.

Stale chunks (split before extract learned to strip) still carry the whole
PG boilerplate. Build must clean chunk heads so no built skill ships them:
the header metadata block (Title/Author/Translator/Release date/Language,
whose *** START marker sits past the 600-char head so the marker strip
never sees it) and the license-tail chunks (whose *** END marker sits past
the head, or in an earlier chunk, so footer prose ships verbatim). A
marker-free notes.md must come out byte-identical.
"""
from pathlib import Path

from book2skill import build as build_mod

# Freud-shaped stale header: the *** START marker sits past the 600-char
# head, exactly like work/freud-dreams/chunks/0000.txt.
HEADER = (
    "The Project Gutenberg eBook of The Interpretation of Dreams\n"
    "    \n"
    "This eBook is for the use of anyone anywhere in the United States and\n"
    "most other parts of the world at no cost and with almost no restrictions\n"
    "whatsoever. You may copy it, give it away or re-use it under the terms\n"
    "of the Project Gutenberg License included with this eBook or online\n"
    "at www.gutenberg.org. If you are not located in the United States,\n"
    "you will have to check the laws of the country where you are located\n"
    "before using this eBook.\n"
    "\n"
    "Title: The Interpretation of Dreams\n"
    "\n"
    "Author: Sigmund Freud\n"
    "\n"
    "Translator: A. A. Brill\n"
    "\n"
    "Release date: August 12, 2021 [eBook #66048]\n"
    "Language: English\n"
    "\n"
    "*** START OF THE PROJECT GUTENBERG EBOOK THE INTERPRETATION OF DREAMS ***\n"
    "\n"
)

# Freud-shaped stale footer: the *** END marker sits past the head of its
# chunk (like 0254.txt line 83), and the license tail fills later chunks
# (like 0255.txt-0258.txt, which open mid-sentence on license prose).
FOOTER_TAIL = (
    "*** END OF THE PROJECT GUTENBERG EBOOK THE INTERPRETATION OF DREAMS ***\n"
    "Updated editions will replace the previous one.\n"
)
LICENSE_CHUNK = (
    "emark license, including paying royalties for use\n"
    "of the Project Gutenberg trademark. If you do not charge anything for\n"
    "copies of this eBook, complying with the trademark license is very\n"
    "easy. You may use this eBook for nearly any purpose.\n"
    "START: FULL LICENSE\n"
    "\n"
    "THE FULL PROJECT GUTENBERG LICENSE\n"
    "1.E.2. If an individual Project Gutenberg electronic work is derived\n"
)
LICENSE_CHUNK_2 = (
    "Contributions to the Project Gutenberg Literary Archive Foundation\n"
    "are tax deductible to the full extent permitted by U.S. law.\n"
    "Most people start at our website which has the main search facility.\n"
)


def test_build_strips_header_metadata_past_the_head(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text(
        HEADER + "Dream analysis opens with free association.\n" * 30,
        encoding="utf-8",
    )
    (work / "chunks" / "0001.txt").write_text(
        "Dream analysis continues with condensation.\n" * 30,
        encoding="utf-8",
    )
    skill = tmp_path / "skill"
    receipt = build_mod.build(work, skill, "skill", "demo description")
    notes = (skill / "chapters" / "notes.md").read_text(encoding="utf-8")
    assert "Gutenberg" not in notes and "gutenberg" not in notes
    assert "*** START OF" not in notes
    for field in ("Title:", "Author:", "Translator:", "Release date:", "Language:"):
        assert field not in notes
    assert "free association" in notes  # body kept
    assert "condensation" in notes
    assert "## 0000" in notes  # section structure kept
    assert receipt["notes_stripped"] is True


def test_build_drops_license_tail_chunks(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text(
        "Dream analysis opens with free association.\n" * 30,
        encoding="utf-8",
    )
    (work / "chunks" / "0001.txt").write_text(
        "Dream analysis closes with displacement.\n" * 20 + FOOTER_TAIL,
        encoding="utf-8",
    )
    (work / "chunks" / "0002.txt").write_text(LICENSE_CHUNK, encoding="utf-8")
    (work / "chunks" / "0003.txt").write_text(LICENSE_CHUNK_2, encoding="utf-8")
    skill = tmp_path / "skill"
    receipt = build_mod.build(work, skill, "skill", "demo description")
    notes = (skill / "chapters" / "notes.md").read_text(encoding="utf-8")
    assert "gutenberg" not in notes.lower()
    for junk in ("START: FULL LICENSE", "FULL LICENSE", "royalties", "tax deductible"):
        assert junk not in notes
    assert "free association" in notes  # body kept
    assert "displacement" in notes  # body before the END marker kept
    assert "## 0000" in notes and "## 0001" in notes
    assert "## 0002" not in notes and "## 0003" not in notes  # tail gone
    assert receipt["notes_stripped"] is True


def test_build_plain_notes_byte_identical(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about leases\n", encoding="utf-8")
    skill = tmp_path / "skill"
    receipt = build_mod.build(work, skill, "skill", "demo description")
    notes = (skill / "chapters" / "notes.md").read_text(encoding="utf-8")
    assert notes == "## 0000\nchapter about leases\n"
    assert receipt["notes_stripped"] is False
    work2 = tmp_path / "work2"
    (work2 / "chunks").mkdir(parents=True)
    (work2 / "chunks" / "0000.txt").write_text("alpha\n", encoding="utf-8")
    (work2 / "chunks" / "0001.txt").write_text("beta", encoding="utf-8")
    build_mod.build(work2, tmp_path / "skill2", "skill2", "demo description")
    notes2 = (tmp_path / "skill2" / "chapters" / "notes.md").read_text(encoding="utf-8")
    assert notes2 == "## 0000\nalpha\n\n\n## 0001\nbeta"
