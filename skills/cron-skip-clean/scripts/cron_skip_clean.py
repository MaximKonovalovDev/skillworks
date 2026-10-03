#!/usr/bin/env python3
"""cron-skip-clean: durable file timer that skips when clean.

Headless, no phone, no network, no prompts. Fingerprints a watch dir;
when the fingerprint matches the state file, prints SKIP and does no
work. On change (or first run), refreshes the state file and prints RUN.

Usage:
    python scripts/cron_skip_clean.py --watch <dir> --state <state.json>

Exit code is always 0 on success; the SKIP/RUN word on stdout is the
contract. State file format is documented in references/state-format.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def fingerprint(watch: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(p for p in watch.rglob("*") if p.is_file())
    for path in files:
        rel = path.relative_to(watch).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    digest.update(f"count={len(files)}".encode("utf-8"))
    return digest.hexdigest()[:16]


def main() -> int:
    parser = argparse.ArgumentParser(description="skip when clean, run when dirty")
    parser.add_argument("--watch", required=True, help="directory to fingerprint")
    parser.add_argument("--state", required=True, help="durable state file (JSON)")
    args = parser.parse_args()

    watch = Path(args.watch)
    if not watch.is_dir():
        print(f"ERROR watch dir missing: {watch}")
        return 2
    state_path = Path(args.state)

    current = fingerprint(watch)
    previous = None
    if state_path.is_file():
        try:
            previous = json.loads(state_path.read_text(encoding="utf-8")).get("fingerprint")
        except (json.JSONDecodeError, UnicodeDecodeError):
            previous = None

    if previous == current:
        print(f"SKIP clean {current}")
        return 0

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"fingerprint": current, "tool": "cron-skip-clean", "version": 1}) + "\n",
        encoding="utf-8",
    )
    print(f"RUN {current}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
