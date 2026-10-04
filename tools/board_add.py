"""Add a board row under the table header, or check the board stays well-formed.

    python tools/board_add.py --id TS-1 --status DOING --scorecard "..." --what "..." --done "..." --owner researcher --evidence "..."
    python tools/board_add.py --check
    python tools/board_add.py --help

A row is one line: no pipe character inside a cell (the keeper skips a
malformed row). --check refuses such a row, a duplicate id, a bad status,
or a DONE row without a commit SHA; exit 1 on any refusal, quoting the rule.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOARD = ROOT / "sprint" / "board.md"
STATUS = {"TOP", "READY", "DOING", "BLOCKED", "OWNER", "DONE"}
HEADER = "| ID | Status | Scorecard row | What | Done when | Owner role | Evidence |"


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def problems(text: str) -> list[str]:
    out: list[str] = []
    lines = [ln for ln in text.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return ["board: no table found"]
    if cells(lines[0]) != cells(HEADER):
        out.append("board: header differs from the keeper shape")
    rows = [cells(ln) for ln in lines[2:]]
    seen: set[str] = set()
    for r in rows:
        if len(r) != 7:
            out.append(f"board: a row has {len(r)} cells, want 7: {r[0] if r else '?'}")
            continue
        rid, status = r[0], r[1]
        if rid in seen:
            out.append(f"board: id twice: {rid} (each id runs once)")
        seen.add(rid)
        if status not in STATUS:
            out.append(f"board: bad status {status} on {rid} (want one of {sorted(STATUS)})")
        if status == "DONE" and not re.search(r"\b[0-9a-f]{7,40}\b", r[6]):
            out.append(f"board: DONE without a commit SHA: {rid} (a DONE row names its commit SHA)")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="refuse a malformed board; write nothing")
    ap.add_argument("--board", default=str(BOARD))
    ap.add_argument("--id", default=None)
    ap.add_argument("--status", default=None)
    ap.add_argument("--scorecard", default=None)
    ap.add_argument("--what", default=None)
    ap.add_argument("--done", default=None)
    ap.add_argument("--owner", default=None)
    ap.add_argument("--evidence", default=None)
    args = ap.parse_args(argv)
    board = Path(args.board)
    try:
        text = board.read_text(encoding="utf-8")
    except OSError:
        print(f"board: cannot read {board}")
        return 1
    if args.check or not args.id:
        bad = problems(text)
        for b in bad:
            print(b)
        print("BOARD CHECK FAIL" if bad else "BOARD CHECK PASS")
        return 1 if bad else 0
    for name in ("status", "scorecard", "what", "done", "owner", "evidence"):
        if getattr(args, name) is None:
            print(f"board_add: missing --{name} (a row carries all seven cells)")
            return 2
    row = [args.id, args.status, args.scorecard, args.what, args.done, args.owner, args.evidence]
    if any("|" in c for c in row):
        print("board_add: refused: no pipe character inside a cell (the keeper skips a malformed row)")
        return 1
    if args.status not in STATUS:
        print(f"board_add: refused: bad status {args.status} (want one of {sorted(STATUS)})")
        return 1
    marker = "|---|---|---|---|---|---|---|"
    if marker not in text:
        print("board_add: refused: header line |---| not found")
        return 1
    line = "| " + " | ".join(row) + " |"
    text = text.replace(marker, marker + "\n" + line, 1)
    bad = problems(text)
    if bad:
        for b in bad:
            print(b)
        return 1
    board.write_text(text, encoding="utf-8")
    print(f"added {args.id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
