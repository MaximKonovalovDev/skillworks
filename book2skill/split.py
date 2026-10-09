"""Split stage: 5k-char Unicode chunks with overlap, or sentence-window chunks."""
from __future__ import annotations

import json
import re
from pathlib import Path

CHUNK = 5000
OVERLAP = 200

CHUNK_MODES = ("chars", "sentences")
SENTENCE_WINDOW = 5
SENTENCE_OVERLAP = 1

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def split_sentences_text(text: str) -> list[str]:
    """Split text into sentences on end punctuation plus whitespace (stdlib only)."""
    stripped = text.strip()
    if not stripped:
        return []
    parts = [s.strip() for s in _SENTENCE_SPLIT_RE.split(stripped) if s.strip()]
    return parts or [stripped]


def chunk_sentences(text: str, window: int = SENTENCE_WINDOW, overlap: int = SENTENCE_OVERLAP) -> list[str]:
    """Sliding window over sentences: window sentences per chunk, overlap kept."""
    if window < 1:
        raise ValueError(f"split: window {window} must be 1 or more")
    if overlap < 0 or overlap >= window:
        raise ValueError(f"split: sent-overlap {overlap} must be 0..window-1 (window {window})")
    sentences = split_sentences_text(text)
    if not sentences:
        return []
    chunks: list[str] = []
    i = 0
    step = window - overlap if window > overlap else 1
    while i < len(sentences):
        piece = " ".join(sentences[i : i + window])
        if piece.strip():
            chunks.append(piece)
        if i + window >= len(sentences):
            break
        i += step
    return chunks


def chunk_text(text: str, mode: str = "chars", chunk: int = CHUNK, overlap: int = OVERLAP,
               window: int = SENTENCE_WINDOW, sent_overlap: int = SENTENCE_OVERLAP) -> list[str]:
    """Chunk one text by mode: chars slices or sentence windows (one home for chunking)."""
    if mode not in CHUNK_MODES:
        raise ValueError(f"split: --chunk-mode {mode} unknown: pick chars or sentences")
    if mode == "sentences":
        return chunk_sentences(text, window=window, overlap=sent_overlap)
    chunks: list[str] = []
    i = 0
    while i < len(text):
        piece = text[i : i + chunk]
        chunks.append(piece)
        if i + chunk >= len(text):
            break
        i += chunk - overlap
    return chunks


def split(workdir: Path, chunk: int = CHUNK, overlap: int = OVERLAP, mode: str = "chars",
          window: int = SENTENCE_WINDOW, sent_overlap: int = SENTENCE_OVERLAP) -> dict:
    src = workdir / "full_text.txt"
    if not src.is_file():
        raise FileNotFoundError(f"split: {src} missing: run extract first")
    text = src.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"split: {src} empty: run extract first")
    if mode not in CHUNK_MODES:
        raise ValueError(f"split: --chunk-mode {mode} unknown: pick chars or sentences")
    chunks = chunk_text(text, mode=mode, chunk=chunk, overlap=overlap, window=window, sent_overlap=sent_overlap)
    if not chunks:
        raise ValueError(f"split: {src} empty: run extract first")
    outdir = workdir / "chunks"
    outdir.mkdir(exist_ok=True)
    for n, piece in enumerate(chunks):
        (outdir / f"{n:04d}.txt").write_text(piece, encoding="utf-8")
    receipt: dict = {"stage": "split", "chunks": len(chunks), "chunk": chunk, "overlap": overlap, "mode": mode}
    if mode == "sentences":
        receipt["window"] = window
        receipt["sent_overlap"] = sent_overlap
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt
