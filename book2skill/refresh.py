"""Refresh stage: fingerprint lock, rebuild index only on change."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from .index import build_index


def fingerprint(workdir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((workdir / "chunks").glob("*.txt")):
        digest.update(path.read_bytes())
    return digest.hexdigest()


# Steal ported fresh from ElromEvedElElyon/atomic-lru-cache (MIT,
# https://github.com/ElromEvedElElyon/atomic-lru-cache/blob/836f95e00b2c4e7f6d5405c1a563b651cd8458ab/src/atomic_lru_cache/cache.py):
# temp+flush+fsync+os.replace atomic write + corrupt-file start-fresh. Rebuilt here in our style etc.
def _atomic_write_text(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# Idea ported fresh from eudicots/Cactus (BSD-3-Clause,
# https://github.com/eudicots/Cactus/blob/main/cactus/site.py):
# fingerprint_extensions config + only-rebuild-changed. Rebuilt here in
# our style as a content-hash compare so refresh and pack zips skip
# stale-ZIP rebuilds when the stored fingerprint matches.
def needs_rebuild(fingerprint_file: Path, current_hash: str) -> bool:
    """True when the stored fingerprint is missing or differs; False when same."""
    if not fingerprint_file.exists():
        return True
    try:
        stored = fingerprint_file.read_text(encoding="utf-8").strip()
    except (OSError, ValueError):
        return True
    return stored != current_hash


def refresh(workdir: Path) -> dict:
    lock = workdir / ".skillworks.lock"
    current = fingerprint(workdir)
    if not needs_rebuild(lock, current):
        receipt = {"stage": "refresh", "changed": False, "fingerprint": current}
        (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        return receipt
    index_receipt = build_index(workdir)
    _atomic_write_text(lock, current)
    receipt = {
        "stage": "refresh",
        "changed": True,
        "fingerprint": current,
        "records": index_receipt.get("records", 0),
    }
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt
