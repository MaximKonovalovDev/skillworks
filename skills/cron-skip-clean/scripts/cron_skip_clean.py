#!/usr/bin/env python3
"""cron-skip-clean: durable file timer that skips when clean.

Headless, no phone, no network, no prompts. Fingerprints a watch dir;
when the fingerprint matches the state file, prints SKIP and does no
work. On change (or first run), refreshes the state file and prints RUN.

Usage:
    python scripts/cron_skip_clean.py --watch <dir> --state <state.json>

Exit code 0 for RUN and SKIP (the first word on stdout is the contract),
2 for a refusal (`ERROR ...` on stdout, the state file is not touched).
State file format is documented in references/state-format.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def fingerprint(watch: Path) -> str:
    """sha256 over the files sorted by relative path (the same order on every OS), 16 hex chars."""
    digest = hashlib.sha256()
    files = sorted((p.relative_to(watch).as_posix(), p) for p in watch.rglob("*") if p.is_file())
    for rel, path in files:
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    digest.update(f"count={len(files)}".encode("utf-8"))
    return digest.hexdigest()[:16]


def previous_fingerprint(state_path: Path) -> str | None:
    """The fingerprint the state file holds, or None when it is missing or unusable (counts as dirty)."""
    if not state_path.is_file():
        return None
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    value = data.get("fingerprint") if isinstance(data, dict) else None
    return value if isinstance(value, str) else None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # a Hebrew name must not crash a pipe set to a legacy code page
    parser = argparse.ArgumentParser(description="skip when clean, run when dirty")
    parser.add_argument("--watch", required=True, help="directory to fingerprint")
    parser.add_argument("--state", required=True, help="durable state file (JSON), outside the watch dir")
    args = parser.parse_args()

    watch = Path(args.watch)
    if not watch.is_dir():
        print(f"ERROR watch dir missing: {watch}")
        return 2
    state_path = Path(args.state)
    if state_path.resolve().is_relative_to(watch.resolve()):
        print(f"ERROR refused: state file {state_path} is inside the watch dir, it would change its own fingerprint and never skip")
        return 2

    try:
        current = fingerprint(watch)
    except OSError as err:
        print(f"ERROR cannot read {err.filename or watch}: {err.strerror}; state untouched")
        return 2
    previous = previous_fingerprint(state_path)

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
