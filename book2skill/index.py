"""Index stage: grounded JSONL knowledge index over chunks.

Retrieval is rarity-weighted substring rank over chunk text. No embeddings,
no vector DB. Each record carries file + offset so answers stay grounded.
"""
from __future__ import annotations

import json
import math
from pathlib import Path


def build_index(workdir: Path) -> dict:
    chunk_files = sorted((workdir / "chunks").glob("*.txt"))
    records = []
    for path in chunk_files:
        text = path.read_text(encoding="utf-8")
        records.append({"file": path.name, "chars": len(text), "head": text[:160]})
    index_path = workdir / "index.jsonl"
    with index_path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    receipt = {"stage": "index", "records": len(records)}
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
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
    paths = sorted((workdir / "chunks").glob("*.txt"))
    texts = [path.read_text(encoding="utf-8").lower() for path in paths]
    total = len(texts)
    if not total:
        return []
    lens = [len(t.split()) or 1 for t in texts]
    avg_len = sum(lens) / total
    doc_freq = {w: sum(1 for text in texts if w in text) for w in words}
    scored = []
    for path, text, doc_len in zip(paths, texts, lens):
        score = 0.0
        for w in words:
            term_freq = text.count(w)
            if not term_freq:
                continue
            n = doc_freq[w]
            idf = math.log(1.0 + (total - n + 0.5) / (n + 0.5))
            norm = k1 * (1.0 - b + b * doc_len / avg_len)
            score += idf * term_freq * (k1 + 1.0) / (term_freq + norm)
        if score:
            scored.append((score, path.name))
    scored.sort(reverse=True)
    return [{"file": name, "score": score} for score, name in scored[:limit]]


def search(workdir: Path, query: str, limit: int = 5) -> list[dict]:
    words = [w.lower() for w in query.split() if len(w) > 2]
    paths = sorted((workdir / "chunks").glob("*.txt"))
    texts = [path.read_text(encoding="utf-8").lower() for path in paths]
    # Rarity (idf) weight so generic query words don't swamp rare terms:
    # weight(w) = log((N+1)/(df+1)) + 1 over chunks; ubiquitous words tend
    # to 1.0 while a term in a handful of chunks scores several times that.
    total = len(texts)
    weights = {}
    for w in words:
        df = sum(1 for text in texts if w in text)
        weights[w] = math.log((total + 1) / (df + 1)) + 1.0
    scored = []
    for path, text in zip(paths, texts):
        score = sum(text.count(w) * weights[w] for w in words)
        if score:
            scored.append((score, path.name))
    scored.sort(reverse=True)
    return [{"file": name, "score": score} for score, name in scored[:limit]]
