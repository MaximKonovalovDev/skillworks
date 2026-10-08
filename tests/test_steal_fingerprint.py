"""Fingerprint-gated rebuild guard: skip stale-ZIP rebuilds when hash matches."""
from pathlib import Path

from book2skill.refresh import needs_rebuild


def test_same_hash_needs_no_rebuild(tmp_path: Path) -> None:
    lock = tmp_path / ".skillworks.lock"
    lock.write_text("abc123", encoding="utf-8")
    assert needs_rebuild(lock, "abc123") is False


def test_different_hash_needs_rebuild(tmp_path: Path) -> None:
    lock = tmp_path / ".skillworks.lock"
    lock.write_text("abc123", encoding="utf-8")
    assert needs_rebuild(lock, "def456") is True


def test_missing_file_needs_rebuild(tmp_path: Path) -> None:
    lock = tmp_path / "missing.lock"
    assert needs_rebuild(lock, "abc123") is True
