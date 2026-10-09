"""Steal port: atomic lock write + corrupt-file start-fresh."""
import os
from pathlib import Path

import pytest

from book2skill.refresh import _atomic_write_text, fingerprint, needs_rebuild, refresh


def _make_work(base: Path) -> Path:
    work = base / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("atomic content", encoding="utf-8")
    return work


def test_corrupt_lock_starts_fresh(tmp_path: Path) -> None:
    work = _make_work(tmp_path)
    lock = work / ".skillworks.lock"
    lock.write_bytes(b"\xff\xfe\x00\x01corrupt\xff")
    assert needs_rebuild(lock, fingerprint(work)) is True
    receipt = refresh(work)
    assert receipt["changed"] is True
    assert lock.read_text(encoding="utf-8") == fingerprint(work)


def test_lock_write_is_atomic_no_temp_left(tmp_path: Path) -> None:
    work = _make_work(tmp_path)
    receipt = refresh(work)
    lock = work / ".skillworks.lock"
    assert lock.read_text(encoding="utf-8") == fingerprint(work)
    assert receipt["fingerprint"] == fingerprint(work)
    leftovers = list(work.glob(".skillworks.lock.*.tmp"))
    assert leftovers == []


def test_failed_replace_leaves_original_intact(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / ".skillworks.lock"
    target.write_text("original", encoding="utf-8")
    def _boom(src: str, dst: str) -> None:
        raise OSError("replace failed")
    monkeypatch.setattr(os, "replace", _boom)
    try:
        _atomic_write_text(target, "new-content")
        assert False, "expected OSError"
    except OSError:
        pass
    assert target.read_text(encoding="utf-8") == "original"
    assert list(tmp_path.glob(".skillworks.lock.*.tmp")) == []


def test_atomic_uses_replace_and_fsync(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / ".skillworks.lock"
    calls = {"replace": 0, "fsync": 0}
    real_replace = os.replace
    real_fsync = os.fsync
    def _record_replace(src: str, dst: str) -> None:
        calls["replace"] += 1
        real_replace(src, dst)
    def _record_fsync(fd: int) -> None:
        calls["fsync"] += 1
        real_fsync(fd)
    monkeypatch.setattr(os, "replace", _record_replace)
    monkeypatch.setattr(os, "fsync", _record_fsync)
    _atomic_write_text(target, "hello")
    assert calls["replace"] == 1
    assert calls["fsync"] == 1
    assert target.read_text(encoding="utf-8") == "hello"
