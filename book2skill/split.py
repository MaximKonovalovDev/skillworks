"""Split stage: 5k-char Unicode chunks with overlap."""
from __future__ import annotations

import json
from pathlib import Path

CHUNK = 5000
OVERLAP = 200


def split(workdir: Path, chunk: int = CHUNK, overlap: int = OVERLAP) -> dict:
    src = workdir / "full_text.txt"
    if not src.is_file():
        raise FileNotFoundError(f"split: {src} missing: run extract first")
    text = src.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"split: {src} empty: run extract first")
    chunks: list[str] = []
    i = 0
    while i < len(text):
        piece = text[i : i + chunk]
        chunks.append(piece)
        if i + chunk >= len(text):
            break
        i += chunk - overlap
    outdir = workdir / "chunks"
    outdir.mkdir(exist_ok=True)
    for n, piece in enumerate(chunks):
        (outdir / f"{n:04d}.txt").write_text(piece, encoding="utf-8")
    receipt = {"stage": "split", "chunks": len(chunks), "chunk": chunk, "overlap": overlap}
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt
