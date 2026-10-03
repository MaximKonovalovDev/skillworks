"""K-09 [BLOCKED-DEEPDIVE-1001]: rarity-weighted substring rank.

Generic query words must not swamp rare terms: the chunk carrying the rare
query terms outranks a chunk repeating only generic query words, even when
the generic chunk has the higher raw substring count (4 vs 3 here).
"""
from pathlib import Path

from book2skill.index import search


def test_rare_term_outranks_generic_word_repetition(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text(
        "what does the dream say what does it mean", encoding="utf-8"
    )
    (work / "chunks" / "0001.txt").write_text(
        "oedipus reveal oedipus", encoding="utf-8"
    )
    (work / "chunks" / "0002.txt").write_text(
        "what does the chapter say", encoding="utf-8"
    )
    (work / "chunks" / "0003.txt").write_text(
        "what does the meadow say", encoding="utf-8"
    )
    hits = search(work, "what does oedipus reveal", limit=4)
    assert [h["file"] for h in hits].index("0001.txt") < [
        h["file"] for h in hits
    ].index("0000.txt")
    assert hits[0]["file"] == "0001.txt"
