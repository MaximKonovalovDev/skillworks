"""Quality slice 4: split fails loudly on bad input."""
from pathlib import Path

import pytest

from book2skill import split as split_mod


def test_split_missing_full_text_raises_with_file_and_reason(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    with pytest.raises(FileNotFoundError, match="full_text"):  # file
        split_mod.split(work)
    try:
        split_mod.split(work)
    except FileNotFoundError as exc:  # reason
        assert "extract" in str(exc).lower(), str(exc)
    else:
        raise AssertionError("missing full_text.txt did not raise")


def test_split_empty_full_text_raises_with_file_and_reason(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    (work / "full_text.txt").write_text("   \n", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):  # reason
        split_mod.split(work)
    try:
        split_mod.split(work)
    except ValueError as exc:  # file
        assert "full_text.txt" in str(exc), str(exc)
    else:
        raise AssertionError("empty full_text.txt did not raise")


def test_split_valid_input_still_chunks(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    (work / "full_text.txt").write_text("hello world, this is real text. " * 10, encoding="utf-8")
    receipt = split_mod.split(work, chunk=50, overlap=5)
    assert receipt["chunks"] >= 1
    assert (work / "chunks" / "0000.txt").is_file()
