'''Index stage: grounded JSONL knowledge index over chunks.

Retrieval is rarity-weighted substring rank over chunk text. No embeddings,
no vector DB. Each record carries file + offset so answers stay grounded.
'''
from __future__ import annotations

import json
import math
from pathlib import Path


_CACHE: dict = {}


def _load_corpus(workdir: Path) -> tuple:
    key = str(Path(workdir).resolve())
    paths = sorted((Path(workdir) / 'chunks').glob('*.txt'))
    stats = [p.stat() for p in paths]
    fp = tuple((p.name, s.st_size, s.st_mtime_ns) for p, s in zip(paths, stats))
    hit = _CACHE.get(key)
    if hit is not None and hit[0] == fp:
        return hit[1], hit[2], hit[3]
    texts = [p.read_text(encoding='utf-8').lower() for p in paths]
    lens = [len(t.split()) or 1 for t in texts]
    _CACHE[key] = (fp, paths, texts, lens)
    return paths, texts, lens


def build_index(workdir: Path) -> dict:
    chunk_files = sorted((workdir / 'chunks').glob('*.txt'))
    records = []
    for path in chunk_files:
        text = path.read_text(encoding='utf-8')
        records.append({'file': path.name, 'chars': len(text), 'head': text[:160]})
    index_path = workdir / 'index.jsonl'
    with index_path.open('w', encoding='utf-8') as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
    receipt = {'stage': 'index', 'records': len(records)}
    (workdir / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    return receipt


# Steal: BM25-lite ranking idea from quickwit-oss/tantivy (MIT,
# https://github.com/quickwit-oss/tantivy/blob/main/LICENSE),
# cf. src/query/bm25.rs: Bm25Weight with K1=1.2, B=0.75 and
# idf = log(1 + (N - n + 0.5) / (n + 0.5)). Fresh pure-python port in
# our substring-count style; search() below is untouched (fallback).
def bm25_search(workdir: Path, query: str, limit: int = 5, k1: float = 1.2, b: float = 0.75) -> list[dict]:
    words = [w.lower() for w in query.split() if len(w) > 2]
    if not words:
        return []
    paths, texts, lens = _load_corpus(workdir)
    total = len(texts)
    if not total:
        return []
    avg_len = sum(lens) / total
    counts = [[text.count(w) for w in words] for text in texts]
    doc_freq = [sum(1 for row in counts if row[j] > 0) for j in range(len(words))]
    idfs = [math.log(1.0 + (total - n + 0.5) / (n + 0.5)) for n in doc_freq]
    norms = [k1 * (1.0 - b + b * doc_len / avg_len) for doc_len in lens]
    scored = []
    for idx, path in enumerate(paths):
        score = 0.0
        row = counts[idx]
        norm = norms[idx]
        for j in range(len(words)):
            tf = row[j]
            if not tf:
                continue
            score += idfs[j] * tf * (k1 + 1.0) / (tf + norm)
        if score:
            scored.append((score, path.name))
    scored.sort(reverse=True)
    return [{'file': name, 'score': score} for score, name in scored[:limit]]


def search(workdir: Path, query: str, limit: int = 5) -> list[dict]:
    words = [w.lower() for w in query.split() if len(w) > 2]
    if not words:
        return []
    paths, texts, _lens = _load_corpus(workdir)
    # Rarity (idf) weight so generic query words do not swamp rare terms:
    # weight(w) = log((N+1)/(df+1)) + 1 over chunks; ubiquitous words tend
    # to 1.0 while a term in a handful of chunks scores several times that.
    total = len(texts)
    if not total:
        return []
    counts = [[text.count(w) for w in words] for text in texts]
    weights = []
    for j, w in enumerate(words):
        df = sum(1 for row in counts if row[j] > 0)
        weights.append(math.log((total + 1) / (df + 1)) + 1.0)
    scored = []
    for path, row in zip(paths, counts):
        s = sum(c * wt for c, wt in zip(row, weights))
        if s:
            scored.append((s, path.name))
    scored.sort(reverse=True)
    return [{'file': name, 'score': score} for score, name in scored[:limit]]

