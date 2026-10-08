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


# Idea ported fresh from eudicots/Cactus (BSD-3-Clause,
# https://github.com/eudicots/Cactus/blob/main/cactus/site.py):
# fingerprint_extensions config + only-rebuild-changed. Rebuilt here in
# our style as a content-hash compare so refresh and pack zips skip
# stale-ZIP rebuilds when the stored fingerprint matches.
def needs_rebuild(fingerprint_file: Path, current_hash: str) -> bool:
    """True when the stored fingerprint is missing or differs; False when same."""
    if not fingerprint_file.exists():
        return True
    stored = fingerprint_file.read_text(encoding="utf-8").strip()
    return stored != current_hash


def refresh(workdir: Path) -> dict:
    lock = workdir / ".skillworks.lock"
    current = fingerprint(workdir)
    if not needs_rebuild(lock, current):
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
