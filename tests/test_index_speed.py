'''Speed pin: optimized search keeps identical output.

Reference copies of the pre-optimization substring rank prove the cached +
fused-count port returns exactly the same files and scores.
'''
from pathlib import Path
import math

from book2skill.index import bm25_search, search


def _ref_search(workdir: Path, query: str, limit: int = 5):
    words = [w.lower() for w in query.split() if len(w) > 2]
    paths = sorted((workdir / 'chunks').glob('*.txt'))
    texts = [p.read_text(encoding='utf-8').lower() for p in paths]
    total = len(texts)
    weights = {}
    for w in words:
        df = sum(1 for t in texts if w in t)
        weights[w] = math.log((total + 1) / (df + 1)) + 1.0
    scored = []
    for path, text in zip(paths, texts):
        score = sum(text.count(w) * weights[w] for w in words)
        if score:
            scored.append((score, path.name))
    scored.sort(reverse=True)
    return [{'file': n, 'score': s} for s, n in scored[:limit]]


def _ref_bm25(workdir: Path, query: str, limit: int = 5, k1: float = 1.2, b: float = 0.75):
    words = [w.lower() for w in query.split() if len(w) > 2]
    if not words:
        return []
    paths = sorted((workdir / 'chunks').glob('*.txt'))
    texts = [p.read_text(encoding='utf-8').lower() for p in paths]
    total = len(texts)
    if not total:
        return []
    lens = [len(t.split()) or 1 for t in texts]
    avg = sum(lens) / total
    freq = {w: sum(1 for t in texts if w in t) for w in words}
    scored = []
    for path, text, ln in zip(paths, texts, lens):
        s = 0.0
        for w in words:
            tf = text.count(w)
            if not tf:
                continue
            nn = freq[w]
            idf = math.log(1.0 + (total - nn + 0.5) / (nn + 0.5))
            norm = k1 * (1.0 - b + b * ln / avg)
            s += idf * tf * (k1 + 1.0) / (tf + norm)
        if s:
            scored.append((s, path.name))
    scored.sort(reverse=True)
    return [{'file': n, 'score': s} for s, n in scored[:limit]]


def _seed(work: Path) -> None:
    c = work / 'chunks'
    c.mkdir(parents=True, exist_ok=True)
    (c / '0000.txt').write_text('what does the dream say what does it mean', encoding='utf-8')
    (c / '0001.txt').write_text('oedipus reveal oedipus', encoding='utf-8')
    (c / '0002.txt').write_text('what does the chapter say', encoding='utf-8')
    (c / '0003.txt').write_text('what does the meadow say', encoding='utf-8')
    (c / '0004.txt').write_text('quokka quokka quokka shared topic words here ' * 4, encoding='utf-8')
    (c / '0005.txt').write_text('shared topic words here and ordinary filler text ' * 8, encoding='utf-8')

_QUERIES = ['what does oedipus reveal', 'quokka shared', 'dream meadow chapter', 'a an of', '', 'what', 'nonexistent zebra xyz', 'shared topic filler words']


def test_search_matches_reference(tmp_path: Path) -> None:
    work = tmp_path / 'work'
    _seed(work)
    for q in _QUERIES:
        assert search(work, q, limit=4) == _ref_search(work, q, limit=4)


def test_bm25_matches_reference(tmp_path: Path) -> None:
    work = tmp_path / 'work'
    _seed(work)
    for q in _QUERIES:
        assert bm25_search(work, q, limit=4) == _ref_bm25(work, q, limit=4)


def test_repeated_calls_hit_cache_identical(tmp_path: Path) -> None:
    work = tmp_path / 'work'
    _seed(work)
    first = search(work, 'quokka shared', limit=4)
    second = search(work, 'quokka shared', limit=4)
    assert first == second == _ref_search(work, 'quokka shared', limit=4)
    first_b = bm25_search(work, 'quokka shared', limit=4)
    second_b = bm25_search(work, 'quokka shared', limit=4)
    assert first_b == second_b == _ref_bm25(work, 'quokka shared', limit=4)


def test_cache_invalidates_on_write(tmp_path: Path) -> None:
    work = tmp_path / 'work'
    _seed(work)
    assert search(work, 'quokka shared', limit=6) == _ref_search(work, 'quokka shared', limit=6)
    (work / 'chunks' / '0005.txt').write_text('quokka quokka quokka quokka quokka brand new rare content', encoding='utf-8')
    assert search(work, 'quokka shared', limit=6) == _ref_search(work, 'quokka shared', limit=6)
    assert bm25_search(work, 'quokka shared', limit=6) == _ref_bm25(work, 'quokka shared', limit=6)

