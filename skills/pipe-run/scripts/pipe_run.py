#!/usr/bin/env python3
"""pipe-run: one-file batch pipeline with a cost cap and dry-run.

Headless, no phone, no network, no prompts. Reads every ``*.txt`` file at
the top level of ``--input`` (sorted, so repeatable), estimates spend as
``chars // 4`` per file (same unit as the audit token estimate), and
refuses to write anything when spend exceeds ``--cap``. ``--dry-run``
prints the plan and changes nothing.

Usage:
    python scripts/pipe_run.py --input <dir> --out <dir> --cap <tokens>
    python scripts/pipe_run.py --input <dir> --out <dir> --cap <tokens> --dry-run

Exit codes: 0 on RUN or DRY-RUN, 2 on over-cap refusal or bad input.
Cost model and output contract live in references/cost-model.md.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def estimate(text: str) -> int:
    """Token estimate for one item: chars // 4, minimum 1."""
    return max(1, len(text) // 4)


def read_item(path: Path) -> str:
    """The item as UTF-8 text with every line break counted as one character, the same on every system."""
    text = path.read_bytes().decode("utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # a Hebrew name must not crash a pipe set to a legacy code page
    parser = argparse.ArgumentParser(description="batch run with cost cap")
    parser.add_argument("--input", required=True, help="input dir of *.txt items (top level only)")
    parser.add_argument("--out", required=True, help="output dir (created on RUN only)")
    parser.add_argument("--cap", required=True, type=int, help="max tokens of spend")
    parser.add_argument("--dry-run", action="store_true", help="plan only, write nothing")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.is_dir():
        print(f"ERROR input dir missing: {src}")
        return 2
    if args.cap < 0:
        print(f"ERROR cap must be >= 0, got {args.cap}")
        return 2
    out = Path(args.out)
    if out.resolve() == src.resolve():
        print(f"ERROR refused: --out is the input dir: {out}")
        return 2
    if out.is_file():
        print(f"ERROR refused: --out is a file: {out}")
        return 2

    items = sorted((p for p in src.iterdir() if p.suffix.lower() == ".txt" and p.is_file()), key=lambda p: p.name)
    costs = []
    for path in items:
        try:
            costs.append((path.name, estimate(read_item(path))))
        except UnicodeDecodeError:
            print(f"ERROR refused: {path.name} is not UTF-8 text; nothing written")
            return 2
        except OSError as err:
            print(f"ERROR refused: cannot read {path.name}: {err.strerror}; nothing written")
            return 2
    spend = sum(cost for _, cost in costs)

    if args.dry_run:
        print(f"DRY-RUN {len(costs)} items spend {spend} tokens (cap {args.cap})")
        return 0

    if spend > args.cap:
        print(
            f"ERROR over cap: spend {spend} tokens > cap {args.cap} tokens, "
            "refused; nothing written"
        )
        return 2

    out.mkdir(parents=True, exist_ok=True)
    for path in items:
        shutil.copyfile(path, out / path.name)
    (out / "receipt.json").write_text(
        json.dumps(
            {"tool": "pipe-run", "items": len(costs), "spend": spend, "cap": args.cap}
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"RUN {len(costs)} items spend {spend}/{args.cap} tokens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
