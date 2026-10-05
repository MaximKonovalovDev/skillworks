"""Seat guard: no untracked files under skills/.

A seat that leaves a new file in skills/ without a board row ships a skill
nobody reviewed. This guard fails on untracked files under skills/ and
passes on a clean tree. It reads `git status --porcelain` (parsed, not
eyeballed), so ignored files (dist/, work/, __pycache__) do not count.

    python tools/seat_guard.py                    # check skills/ in this repo
    python tools/seat_guard.py --skills skills --root .

Prints each untracked path, then RESULT PASS (clean) or RESULT FAIL.
Exit 0 clean, 1 untracked files, 2 git or usage error. Offline, no writes.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def untracked_skills(root: Path, skills_rel: str) -> list[str]:
    """Untracked paths under the skills dir, via NUL-separated porcelain status."""
    r = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--", skills_rel],
        cwd=root, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"git status failed: {r.stderr.strip() or r.stdout.strip()}")
    out: list[str] = []
    for entry in r.stdout.split("\0"):
        if len(entry) < 4 or not entry.startswith("??"):
            continue
        path = entry[3:].strip()
        if not path:
            continue
        full = root / path
        if full.is_dir():
            # git collapses a fully untracked dir to one line: expand it so the
            # seat sees the files it left behind.
            files = sorted(p.relative_to(root).as_posix()
                           for p in sorted(full.rglob("*")) if p.is_file())
            out.extend(files or [path])
        else:
            out.append(path)
    return sorted(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ROOT), help="repo root (default this repo)")
    ap.add_argument("--skills", default="skills", help="skills dir (default skills)")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    skills = Path(args.skills)
    skills_dir = skills if skills.is_absolute() else root / skills
    if not skills_dir.is_dir():
        print(f"ERROR skills dir missing: {skills_dir}")
        return 2
    try:
        rel = skills_dir.relative_to(root).as_posix()
    except ValueError:
        print(f"ERROR skills dir {skills_dir} is outside root {root}")
        return 2
    try:
        bad = untracked_skills(root, rel)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ERROR {exc}")
        return 2
    for path in bad:
        print(f"UNTRACKED {path}")
    if bad:
        print(f"RESULT FAIL: {len(bad)} untracked files under {rel}/ (add a board row or remove them)")
        return 1
    print(f"RESULT PASS: no untracked files under {rel}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
