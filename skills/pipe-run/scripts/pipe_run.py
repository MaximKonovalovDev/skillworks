#!/usr/bin/env python3
"""pipe-run: one-file batch pipeline with a cost cap and dry-run.

Headless, no phone, no network, no prompts. Reads every ``*.txt`` file in
``--input`` (sorted, so repeatable), estimates spend as ``chars // 4``
per file (same unit as the audit token estimate), and refuses to write
anything when spend exceeds ``--cap``. ``--dry-run`` prints the plan and
changes nothing.

Usage:
    python scripts/pipe_run.py --input <dir> --out <dir> --cap <tokens>
    python scripts/pipe_run.py --input <dir> --out <dir> --cap <tokens> --dry-run

Exit codes: 0 on RUN or DRY-RUN, 2 on over-cap refusal or bad input.
Cost model and output contract live in references/cost-model.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def estimate(text: str) -> int:
    """Token estimate for one item: chars // 4, minimum 1."""
    return max(1, len(text) // 4)


def main() -> int:
    parser = argparse.ArgumentParser(description="batch run with cost cap")
    parser.add_argument("--input", required=True, help="input dir of *.txt items")
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

    items = sorted(p for p in src.glob("*.txt") if p.is_file())
    costs = [(p.name, estimate(p.read_text(encoding="utf-8"))) for p in items]
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

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for path in items:
        (out / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
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
