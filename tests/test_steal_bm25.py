"""Steal check: tantivy BM25-lite ranking port in book2skill/index.py."""
import math

from pathlib import Path

from book2skill.index import bm25_search, search


def _seed(workdir: Path) -> None:
    chunks = workdir / "chunks"
    chunks.mkdir(parents=True, exist_ok=True)
    (chunks / "rare_many.txt").write_text("quokka quokka quokka shared topic words here " * 4, encoding="utf-8")
    (chunks / "rare_once.txt").write_text("quokka plus many other shared topic words here " * 6, encoding="utf-8")
    for i in range(6):
        (chunks / ("filler_%d.txt" % i)).write_text("shared topic words here and ordinary filler text " * 8, encoding="utf-8")


def test_bm25_prefers_more_rare_term_hits(tmp_path: Path) -> None:
    _seed(tmp_path)
    ranked = bm25_search(tmp_path, "quokka shared")
    assert ranked[0]["file"] == "rare_many.txt"


def test_bm25_scores_finite(tmp_path: Path) -> None:
    _seed(tmp_path)
    rows = bm25_search(tmp_path, "quokka shared")
    assert rows
    for row in rows:
        assert math.isfinite(row["score"])
        assert row["score"] > 0


def test_old_search_still_works(tmp_path: Path) -> None:
    _seed(tmp_path)
    ranked = search(tmp_path, "quokka shared")
    assert ranked
    assert ranked[0]["file"] == "rare_many.txt"
