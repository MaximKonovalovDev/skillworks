#!/usr/bin/env python3
"""inbox-file-reader: file one inbox item to a board file, touch nothing else.

Headless, no phone, no network, no prompts. Reads ONLY the ``--inbox``
file, takes its first non-empty line, appends it to the ``--board``
file as one board line, and removes the filed line from the inbox.

Usage:
    python scripts/file_one_item.py --inbox <inbox.md> --board <board.md>

Path allowlist: both paths must end in ``.md``, ``.markdown`` or
``.txt``. Anything else (e.g. a ``.py`` code file) is refused with
exit 2 and nothing is written. ``--inbox`` and ``--board`` must not
resolve to the same file. The board line format and refusal contract
live in references/isolation.md.

Exit codes: 0 on FILED, 2 on refusal (bad path, missing/empty inbox).
"""
from __future__ import annotations

import argparse
from pathlib import Path

ALLOWED_SUFFIXES = {".md", ".markdown", ".txt"}
BOARD_PREFIX = "- [ ] "


def allowed(path: Path) -> bool:
    """Allowlist check: inbox/board must be plain text inbox files."""
    return path.suffix.lower() in ALLOWED_SUFFIXES


def main() -> int:
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
        print(f"ERROR inbox missing: {inbox}")
        return 2

    text = inbox.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
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

    board_line = f"{BOARD_PREFIX}{item}\n"
    if board.parent != Path(".") and str(board.parent):
        board.parent.mkdir(parents=True, exist_ok=True)
    with board.open("a", encoding="utf-8") as handle:
        handle.write(board_line)

    remaining = [line for i, line in enumerate(lines) if i != item_index]
    inbox.write_text("".join(remaining), encoding="utf-8")

    print(f"FILED {item} -> {board}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
