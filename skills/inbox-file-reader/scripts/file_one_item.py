#!/usr/bin/env python3
"""inbox-file-reader: file one inbox item to a board file, touch nothing else.

Headless, no phone, no network, no prompts. Reads the ``--inbox`` file
(and the line breaks at the end of ``--board``), takes the first
non-empty line of the inbox, appends it to the ``--board`` file as one
board line, and removes the filed line from the inbox. Every other line
of both files stays as it was, byte for byte.

Usage:
    python scripts/file_one_item.py --inbox <inbox.md> --board <board.md>

Path allowlist: both paths must end in ``.md``, ``.markdown`` or
``.txt``. Anything else (e.g. a ``.py`` code file) is refused with
exit 2 and nothing is written. ``--inbox`` and ``--board`` must not
resolve to the same file. The board line format and refusal contract
live in references/isolation.md.

Exit codes: 0 on FILED, 2 on refusal (bad path, missing, empty or
non-UTF-8 inbox).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ALLOWED_SUFFIXES = {".md", ".markdown", ".txt"}
BOARD_PREFIX = "- [ ] "
BOM = b"\xef\xbb\xbf"


def allowed(path: Path) -> bool:
    """Allowlist check: inbox/board must be plain text inbox files."""
    return path.suffix.lower() in ALLOWED_SUFFIXES


def split_lines(text: str) -> list[str]:
    """Lines with their own line break kept; only \\n ends a line (a \\r before it stays with the line)."""
    return re.findall(r"[^\n]*\n|[^\n]+", text)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # a Hebrew name must not crash a pipe set to a legacy code page
    parser = argparse.ArgumentParser(description="file one inbox item to a board")
    parser.add_argument("--inbox", required=True, help="inbox file to read one item from")
    parser.add_argument("--board", required=True, help="board file to append one line to")
    args = parser.parse_args()

    inbox = Path(args.inbox)
    board = Path(args.board)

    for label, path in (("inbox", inbox), ("board", board)):
        if not allowed(path):
            print(f"ERROR refused: {label} path outside allowlist: {path}")
            return 2

    try:
        same = inbox.resolve() == board.resolve()
    except OSError:
        same = False
    if same:
        print(f"ERROR refused: inbox and board are the same file: {inbox}")
        return 2

    if not inbox.is_file():
        print(f"ERROR inbox missing: {inbox}; board untouched")
        return 2

    try:
        raw = inbox.read_bytes()
        has_bom = raw.startswith(BOM)
        lines = split_lines((raw[len(BOM):] if has_bom else raw).decode("utf-8"))
    except UnicodeDecodeError:
        print(f"ERROR inbox is not UTF-8 text: {inbox}; board untouched")
        return 2
    except OSError as err:
        print(f"ERROR cannot read inbox {inbox}: {err.strerror}; board untouched")
        return 2

    item: str | None = None
    item_index: int | None = None
    for i, line in enumerate(lines):
        if line.strip():
            item = line.strip()
            item_index = i
            break
    if item is None or item_index is None:
        print(f"ERROR inbox empty: {inbox}; board untouched")
        return 2

    # Keep the board's own style: its line break, and a break before ours when its last line has none.
    try:
        existing = board.read_bytes() if board.is_file() else b""
        newline = "\r\n" if b"\r\n" in existing else "\n"
        lead = newline if existing and not existing.endswith(b"\n") else ""
        board.parent.mkdir(parents=True, exist_ok=True)
        with board.open("ab") as handle:
            handle.write(f"{lead}{BOARD_PREFIX}{item}{newline}".encode("utf-8"))
    except OSError as err:
        print(f"ERROR cannot write board {board}: {err.strerror}; inbox untouched")
        return 2

    remaining = "".join(line for i, line in enumerate(lines) if i != item_index)
    inbox.write_bytes((BOM if has_bom else b"") + remaining.encode("utf-8"))

    print(f"FILED {item} -> {board}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
