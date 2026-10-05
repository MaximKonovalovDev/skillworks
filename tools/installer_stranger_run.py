"""Stranger install run: the 15-minute install from the lock, with an empty-diff check.

A stranger with this repo and Python can prove the pinned installer works in
about 15 minutes, offline (stdlib plus tools/skill_registry.py only, no
network, no writes outside temp dirs unless --apply is passed):

    python tools/skill_registry.py freeze --skills skills --manifest m.json --lock l.json
    python tools/skill_registry.py install --lock l.json --source skills --to <dir>
    python tools/skill_registry.py install --lock l.json --source skills --to <dir> --check

This script runs those three steps and checks the last one shows an empty
diff (RESULT CONVERGED). Dry-run default: freeze and install go to temp dirs
that are deleted after. Pass --apply --to <dir> to converge a real dir.

    python tools/installer_stranger_run.py                       # dry run, temp dirs
    python tools/installer_stranger_run.py --lock l.json          # dry run from a lock file
    python tools/installer_stranger_run.py --apply --to <dir>     # converge <dir> from a fresh lock

Exit 0 on empty diff, 1 on any diff or error. Never reads or writes the
network. Refuses a --to inside the skills dir (a nested output crashed the
OpenCode server 9 times).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REGISTRY = HERE / "skill_registry.py"


def run(*args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(REGISTRY), *args], cwd=ROOT,
                       capture_output=True, text=True, timeout=300)
    return r.returncode, (r.stdout + r.stderr).strip()


def inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skills", default="skills", help="skills source dir (default skills)")
    ap.add_argument("--lock", default=None, help="lock file to install from (default: freeze a fresh one)")
    ap.add_argument("--to", default=None, help="destination dir (default: a temp dir; required with --apply)")
    ap.add_argument("--apply", action="store_true",
                    help="converge --to for real (default is a dry run in temp dirs, nothing kept)")
    ap.add_argument("skills_only", nargs="*", help="install only these skills (default: all in the lock)")
    args = ap.parse_args(argv)

    skills_dir = (ROOT / args.skills).resolve() if not Path(args.skills).is_absolute() else Path(args.skills)
    if not (skills_dir / "SKILL.md").parent.is_dir() or not skills_dir.is_dir():
        print(f"ERROR skills dir missing: {skills_dir}")
        return 1
    if args.apply and not args.to:
        print("ERROR refused: --apply needs --to <dir> (dry run otherwise, nothing is written)")
        return 1
    if args.to:
        dest = Path(args.to).resolve()
        if inside(dest, skills_dir.resolve()) or dest == skills_dir.resolve():
            print(f"ERROR refused: --to {dest} is inside skills/ (a nested output crashed the OpenCode server 9 times)")
            return 1
    names = args.skills_only

    print("stranger run: 15-minute install from the lock, empty-diff check (offline, dry run by default)")
    with tempfile.TemporaryDirectory(prefix="stranger-run-") as tmp:
        tmpdir = Path(tmp)
        lock = Path(args.lock).resolve() if args.lock else tmpdir / "lock.json"
        manifest = tmpdir / "manifest.json"
        if args.lock:
            if not lock.is_file():
                print(f"ERROR cannot read lock {lock}")
                return 1
            print(f"step 1/3 (~1 min): use lock {lock}")
        else:
            print("step 1/3 (~2 min): freeze a fresh manifest + lock from skills/")
            code, out = run("freeze", "--skills", str(skills_dir),
                            "--manifest", str(manifest), "--lock", str(lock), *names)
            print(out)
            if code != 0:
                print("RESULT STALE: freeze failed")
                return 1
        if args.apply:
            dest = Path(args.to).resolve()  # checked above
            print(f"step 2/3 (~5 min): install --apply from lock to {dest}")
            code, out = run("install", "--lock", str(lock), "--source", str(skills_dir),
                            "--to", str(dest), *names)
            print(out)
            if code != 0:
                print("RESULT STALE: install did not converge")
                return 1
            print(f"step 3/3 (~1 min): empty-diff check on {dest}")
            code, out = run("install", "--lock", str(lock), "--source", str(skills_dir),
                            "--to", str(dest), "--check", *names)
            print(out)
            print("RESULT CONVERGED: install from lock, empty diff" if code == 0
                  else "RESULT STALE: diff remains after install")
            return code
        dest = tmpdir / "installed"
        print("step 2/3 (~5 min): install from lock into a temp dir (dry run, nothing kept)")
        code, out = run("install", "--lock", str(lock), "--source", str(skills_dir),
                        "--to", str(dest), *names)
        print(out)
        if code != 0:
            print("RESULT STALE: install did not converge")
            return 1
        print("step 3/3 (~1 min): empty-diff check on the temp dir")
        code, out = run("install", "--lock", str(lock), "--source", str(skills_dir),
                        "--to", str(dest), "--check", *names)
        print(out)
        print("RESULT CONVERGED: install from lock, empty diff (dry run, nothing written)" if code == 0
              else "RESULT STALE: diff remains after install")
        return code


if __name__ == "__main__":
    sys.exit(main())
