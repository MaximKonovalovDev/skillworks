"""Gutenberg normalize: plain-text cleanup for public-domain etexts (SK-08).

Strips the Project Gutenberg header/footer markers plus the metadata
layout (Title/Author/Release_Date block and licence-tail openers) from
one text. Plain notes with no markers and no metadata pass through
byte-identical.

Ideas only, own code: the marker-strip idea mirrors the MIT
gutenberg-dammit normalize shape; parsing is stdlib only (no ebooklib).
No donor code is copied.

Command::

    python tools/gutenberg_normalize.py --in <file> --out <file>

Prints chars plus whether a strip fired. Exit 0 always (use --check to
fail when a strip fires). When nothing fires, --out is byte-identical
to --in.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

START_MARKERS = (
    "*** START OF THE PROJECT GUTENBERG",
    "*** START OF THIS PROJECT GUTENBERG",
)
END_MARKERS = (
    "*** END OF THE PROJECT GUTENBERG",
    "*** END OF THIS PROJECT GUTENBERG",
)
HEAD_SCAN_LINES = 600
END_MIN_LINE = 100

META_PREFIXES = (
    "title:",
    "author:",
    "editor:",
    "translator:",
    "illustrator:",
    "release date:",
    "release-date:",
    "language:",
    "character set encoding:",
    "character set:",
    "produced by:",
    "transcriber:",
)
BLURB_HINTS = (
    "project gutenberg",
    "gutenberg.org",
    "this ebook is for the use of anyone",
    "at no cost and with almost no restrictions",
    "you may copy it, give it away or re-use it",
    "check the laws of the country",
    "most people start at our website",
)
TAIL_HINTS = (
    "START: FULL LICENSE",
    "FULL PROJECT GUTENBERG",
)


def _is_meta(line: str) -> bool:
    low = line.strip().lower()
    if not low:
        return True  # blank top lines are layout, not prose
    if low.startswith(META_PREFIXES):
        return True
    return any(h in low for h in BLURB_HINTS)


def normalize(text: str) -> tuple[str, bool]:
    """Return (cleaned, stripped). Unmarked plain text comes back unchanged."""
    lines = text.splitlines()
    start = 0
    fired = False
    for i, line in enumerate(lines[:HEAD_SCAN_LINES]):
        if any(m in line for m in START_MARKERS):
            start = i + 1
            fired = True
            break
    kept_from = start
    while kept_from < len(lines) and _is_meta(lines[kept_from]):
        kept_from += 1
    if kept_from > start:
        fired = True
    start = kept_from
    end = len(lines)
    for j in range(start, len(lines)):
        if j >= END_MIN_LINE and any(m in lines[j] for m in END_MARKERS):
            end = j
            fired = True
            break
    else:
        for k in range(start, len(lines)):
            if any(h in lines[k] for h in TAIL_HINTS):
                end = k
                fired = True
                break
    while end > start and _is_meta(lines[end - 1]):
        end -= 1
        fired = True
    if not fired:
        return text, False
    return "\n".join(lines[start:end]).strip(), True


def normalize_bytes(data: bytes) -> tuple[bytes, bool]:
    """Byte path: plain input returns the same bytes."""
    text = data.decode("utf-8", errors="replace")
    out, fired = normalize(text)
    if not fired:
        return data, False
    return out.encode("utf-8"), True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="src", required=True, help="input text file")
    ap.add_argument("--out", required=True, help="output text file")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when a strip fires (gate mode)")
    args = ap.parse_args(argv)
    raw = Path(args.src).read_bytes()
    clean, fired = normalize_bytes(raw)
    Path(args.out).write_bytes(clean)
    print(f"normalized {len(clean)} chars (stripped {fired})")
    print("RESULT PASS" if not (args.check and fired) else "RESULT FAIL")
    return 1 if (args.check and fired) else 0


if __name__ == "__main__":
    raise SystemExit(main())
