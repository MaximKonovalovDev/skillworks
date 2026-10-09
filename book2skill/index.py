'''Index stage: grounded JSONL knowledge index over chunks.

Retrieval is rarity-weighted substring rank over chunk text. No embeddings,
no vector DB. Each record carries file + offset so answers stay grounded.
'''
from __future__ import annotations

import json
import math
import os
from pathlib import Path


_CACHE: dict = {}


def _load_corpus(workdir: Path) -> tuple:
    key = str(Path(workdir).resolve())
    chunk_dir = Path(workdir) / 'chunks'
    try:
        with os.scandir(chunk_dir) as it:
            entries = [(e.name, e.stat()) for e in it if e.name.endswith('.txt') and e.is_file()]
    except FileNotFoundError:
        entries = []
    rows = sorted((name, st.st_size, st.st_mtime_ns) for name, st in entries)
    fp = tuple(rows)
    hit = _CACHE.get(key)
    if hit is not None and hit[0] == fp:
        return hit[1], hit[2], hit[3]
    paths = [chunk_dir / name for name, _size, _mtime in rows]
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


# Steal: precomputed doc_freqs/idf + subset batch scoring from
# dorianbrown/rank_bm25 (Apache-2.0,
# https://github.com/dorianbrown/rank_bm25/blob/master/rank_bm25.py,
# LICENSE https://github.com/dorianbrown/rank_bm25/blob/master/LICENSE)
# BM25Okapi.get_batch_scores: score only docs containing query terms.
_BM25_PRE: dict = {}


def _bm25_precomp(workdir: Path) -> tuple:
    key = str(Path(workdir).resolve())
    paths, texts, lens = _load_corpus(workdir)
    fp = _CACHE[key][0]
    hit = _BM25_PRE.get(key)
    if hit is not None and hit[0] == fp:
        return hit[1]
    total = len(texts)
    tfs: list = []
    doc_freqs: dict = {}
    postings: dict = {}
    for idx, text in enumerate(texts):
        ctr: dict = {}
        for tok in text.split():
            ctr[tok] = ctr.get(tok, 0) + 1
        tfs.append(ctr)
        for tok in ctr:
            doc_freqs[tok] = doc_freqs.get(tok, 0) + 1
            postings.setdefault(tok, []).append(idx)
    avg_len = (sum(lens) / total) if total else 0.0
    idfs = {t: math.log(1.0 + (total - n + 0.5) / (n + 0.5)) for t, n in doc_freqs.items()}
    bundle = (paths, texts, tfs, lens, avg_len, doc_freqs, idfs, postings)
    _BM25_PRE[key] = (fp, bundle)
    return bundle


def bm25_batch_search(workdir: Path, query: str, limit: int = 5, k1: float = 1.2, b: float = 0.75, doc_ids=None) -> list[dict]:
    words = [w.lower() for w in query.split() if len(w) > 2]
    if not words:
        return []
    pre = _bm25_precomp(workdir)
    paths, texts, tfs, lens, avg_len, doc_freqs, idfs, postings = pre
    total = len(paths)
    if not total or not avg_len:
        return []
    oov = [w for w in words if w not in doc_freqs]
    oov_df: dict = {}
    oov_idf: dict = {}
    if oov:
        for w in oov:
            n = sum(1 for t in texts if w in t)
            oov_df[w] = n
            oov_idf[w] = math.log(1.0 + (total - n + 0.5) / (n + 0.5))
    if doc_ids is None:
        cand_set = set()
        for w in words:
            lst = postings.get(w)
            if lst:
                cand_set.update(lst)
        for w in oov:
            if oov_df[w]:
                for idx, t in enumerate(texts):
                    if idx not in cand_set and w in t:
                        cand_set.add(idx)
        cand = sorted(cand_set)
    else:
        cand = sorted({i for i in doc_ids if 0 <= i < total})
    if not cand:
        return []
    q_idfs = [(idfs[w] if w in idfs else oov_idf[w]) for w in words]
    scored = []
    for idx in cand:
        ctr = tfs[idx]
        norm = k1 * (1.0 - b + b * lens[idx] / avg_len)
        score = 0.0
        text = None
        for j, w in enumerate(words):
            tf = ctr.get(w, 0)
            if tf == 0 and w in oov_df and oov_df[w]:
                if text is None:
                    text = texts[idx]
                tf = text.count(w)
            if not tf:
                continue
            score += q_idfs[j] * tf * (k1 + 1.0) / (tf + norm)
        if score:
            scored.append((score, paths[idx].name))
    scored.sort(reverse=True)
    return [{"file": name, "score": score} for score, name in scored[:limit]]


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

