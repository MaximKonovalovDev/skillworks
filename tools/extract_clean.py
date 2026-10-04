"""extract_clean (TS-4): clean extract of a PDF, EPUB or DOCX you own.

markitdown engine keeps headings, pipe tables and fenced code; classic is the
plain-text fallback; auto tries markitdown first. Prints chars, kind, engine
and the heading/table/fence counts from the receipt.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from book2skill import extract as extract_mod


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="src", required=True, help="PDF/EPUB/DOCX you own")
    ap.add_argument("--out", required=True, help="work dir, e.g. work/mybook")
    ap.add_argument("--engine", default="markitdown",
                    choices=["classic", "markitdown", "auto"],
                    help="markitdown keeps headings, tables and code fences")
    ap.add_argument("--glob", default=None, help="docs folder only: file pattern")
    args = ap.parse_args(argv)
    try:
        receipt = extract_mod.extract(args.src, Path(args.out), include=args.glob, engine=args.engine)
    except ValueError as exc:
        print(f"extract_clean: {exc}", file=sys.stderr)
        return 2
    print(f"extracted {receipt['chars']} chars ({receipt['kind']}, engine {receipt['engine']}; "
          f"headings {receipt['md_headings']} tables {receipt['md_tables']} fences {receipt['md_fences']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
