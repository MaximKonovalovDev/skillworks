"""Steal check: precomputed-idf + subset BM25 batch scoring (rank_bm25 port)."""
import time
import warnings
from pathlib import Path

from book2skill.index import bm25_batch_search, bm25_search


def _seed_500(workdir: Path) -> None:
    chunks = workdir / "chunks"
    chunks.mkdir(parents=True, exist_ok=True)
    filler = ("alpha bravo charlie delta echo foxtrot golf hotel india juliet "
              "kilo lima mike november oscar papa quebec romeo sierra tango "
              "uniform victor whiskey xray yankee zulu river stone cloud meadow")
    for i in range(500):
        words = [filler] * 64
        if i % 97 == 0:
            words.append("quokka quokka quokka")
        if i % 131 == 0:
            words.append("zephyr zephyr")
        (chunks / ("chunk_%04d.txt" % i)).write_text(" ".join(words), encoding="utf-8")


def _time(fn, *args, repeats=5):
    fn(*args)  # warm cache
    start = time.perf_counter()
    for _ in range(repeats):
        fn(*args)
    return (time.perf_counter() - start) / repeats


def test_batch_matches_old_ranking(tmp_path: Path) -> None:
    work = tmp_path / "work"
    _seed_500(work)
    queries = ["quokka zephyr", "alpha bravo", "river stone cloud", "nonexistent zebra xyz"]
    for q in queries:
        old = bm25_search(work, q, limit=5)
        new = bm25_batch_search(work, q, limit=5)
        assert [r["file"] for r in new] == [r["file"] for r in old]
        assert [r["score"] for r in new] == [r["score"] for r in old]


def test_batch_subset_doc_ids(tmp_path: Path) -> None:
    work = tmp_path / "work"
    _seed_500(work)
    full = bm25_batch_search(work, "quokka zephyr", limit=500)
    assert full
    sub = bm25_batch_search(work, "quokka zephyr", limit=500, doc_ids=[0, 1, 2])
    assert sub
    names = [r["file"] for r in sub]
    assert set(names) <= {"chunk_0000.txt", "chunk_0001.txt", "chunk_0002.txt"}


def test_batch_faster_than_old_path(tmp_path: Path) -> None:
    work = tmp_path / "work"
    _seed_500(work)
    query = "quokka zephyr"
    before = _time(bm25_search, work, query, repeats=5)
    after = _time(bm25_batch_search, work, query, repeats=5)
    msg = "bm25 timing before=%.4fs after=%.4fs" % (before, after)
    print(msg)
    warnings.warn(msg)
    assert after < before
