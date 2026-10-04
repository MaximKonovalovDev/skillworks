"""Copy fleet skills out of this repo (the source) into a folder an agent reads skills from.

    python tools/install_fleet_skills.py --to <skills dir> [skill ...]          # copy, report what changed
    python tools/install_fleet_skills.py --to <skills dir> --check [skill ...]  # exit 1 when a copy is stale

Where OpenCode 1.18 looks (read from its own code and `opencode debug skill`, 2026-10-03):
  <repo>/.opencode/skills/<name>/SKILL.md      one repo
  <home>/.config/opencode/skills/<name>/SKILL.md   every repo on the PC (global)
Never keep the same skill name in both places: OpenCode logs a duplicate and the later one wins.

A copy holds SKILL.md, references/*.md and the scripts the skill names. The test and proof files stay here.
With no skill names, every fleet skill that is built is copied.
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
FLEET = ["pwsh-for-bash-writers", "git-one-branch", "real-browser-automation", "bevy-rust-ecs", "engine-builder", "repo-read-first", "edit-reread"]
# Source-only files: the pair list and its checker, and the proof that the live tests passed.
SKIP_FILES = {"live-proof.json", "pairs.json", "run_pairs.py", "pairs_to_md.py"}
SKIP_DIRS = {"export", "__pycache__", ".pytest_cache"}


def payload(name: str) -> list[Path]:
    """Relative paths of the files a copy of the skill holds."""
    base = SKILLS / name
    out = []
    for p in sorted(base.rglob("*")):
        rel = p.relative_to(base)
        if not p.is_file() or p.name in SKIP_FILES or SKIP_DIRS & set(rel.parts):
            continue
        out.append(rel)
    return out


def stale(name: str, dest_root: Path) -> list[str]:
    """What differs between the source and the copy: missing, changed or extra files."""
    base, dest = SKILLS / name, dest_root / name
    want = payload(name)
    problems = []
    for rel in want:
        target = dest / rel
        if not target.is_file():
            problems.append(f"missing {rel.as_posix()}")
        elif not filecmp.cmp(base / rel, target, shallow=False):
            problems.append(f"changed {rel.as_posix()}")
    if dest.is_dir():
        have = {p.relative_to(dest) for p in dest.rglob("*") if p.is_file()}
        problems += [f"extra {rel.as_posix()}" for rel in sorted(have - set(want))]
    return problems


def install(name: str, dest_root: Path) -> list[str]:
    base, dest = SKILLS / name, dest_root / name
    changes = stale(name, dest_root)
    for rel in payload(name):
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(base / rel, target)
    for line in changes:
        if line.startswith("extra "):
            (dest / line[6:]).unlink()
    return changes


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--to", required=True, help="skills folder to install into (its children are the skill folders)")
    ap.add_argument("--check", action="store_true", help="only compare; exit 1 when a copy is stale")
    ap.add_argument("skills", nargs="*")
    args = ap.parse_args(argv)
    names = args.skills or [n for n in FLEET if (SKILLS / n / "SKILL.md").is_file()]
    unknown = [n for n in names if not (SKILLS / n / "SKILL.md").is_file()]
    if unknown:
        print(f"not built here: {unknown}")
        return 2
    dest_root = Path(args.to)
    worst = 0
    for name in names:
        if args.check:
            problems = stale(name, dest_root)
            print(f"{'STALE' if problems else 'ok   '} {name}: {'; '.join(problems) if problems else 'copy matches the source'}")
            worst = 1 if problems else worst
        else:
            changes = install(name, dest_root)
            print(f"{'updated' if changes else 'current'} {name} -> {dest_root / name}: {'; '.join(changes) if changes else 'nothing to change'}")
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
