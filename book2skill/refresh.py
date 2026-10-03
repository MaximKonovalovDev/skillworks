"""Refresh stage: fingerprint lock, rebuild index only on change."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .index import build_index


def fingerprint(workdir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((workdir / "chunks").glob("*.txt")):
        digest.update(path.read_bytes())
    return digest.hexdigest()


def refresh(workdir: Path) -> dict:
    lock = workdir / ".skillworks.lock"
    current = fingerprint(workdir)
    if lock.exists() and lock.read_text(encoding="utf-8").strip() == current:
        receipt = {"stage": "refresh", "changed": False, "fingerprint": current}
        (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        return receipt
    index_receipt = build_index(workdir)
    lock.write_text(current, encoding="utf-8")
    receipt = {
        "stage": "refresh",
        "changed": True,
        "fingerprint": current,
        "records": index_receipt.get("records", 0),
    }
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt
