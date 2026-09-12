"""Index stage: grounded JSONL knowledge index over chunks.

Retrieval is substring rank over chunk text. No embeddings, no vector DB.
Each record carries file + offset so answers stay grounded.
"""
from __future__ import annotations

import json
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


def search(workdir: Path, query: str, limit: int = 5) -> list[dict]:
    words = [w.lower() for w in query.split() if len(w) > 2]
    scored = []
    for path in sorted((workdir / "chunks").glob("*.txt")):
        text = path.read_text(encoding="utf-8").lower()
        score = sum(text.count(w) for w in words)
        if score:
            scored.append((score, path.name))
    scored.sort(reverse=True)
    return [{"file": name, "score": score} for score, name in scored[:limit]]
