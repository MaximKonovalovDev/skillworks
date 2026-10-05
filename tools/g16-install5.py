"""G-16 installer to 5 repos (dry run, offline).

Proves the fleet installer shape converges in each of 5 repos without
touching them: for each repo it runs the read-only empty-diff check from
tools/install_fleet_skills.py (stale per skill) and it proves the shape
converges in a temp dir (install then check shows an empty diff).

    python tools/g16-install5.py                 # dry run, nothing kept
    python tools/g16-install5.py --check         # dry run, exit 1 when a repo is stale
    python tools/g16-install5.py forge           # dry run for one repo only
    python tools/g16-install5.py --apply --to <dir>   # converge <dir> for real, then check

Exit 0 on dry-run proof converged (or on --apply converged). With --check,
exit 1 when any repo shows a diff. Never uses the network. Dry run never
writes outside temp dirs. Refuses a --to inside skills/ (a nested output
crashed the OpenCode server 9 times).
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SKILLS_DIR = ROOT / "skills"

# The 5 repos the installer serves (loads bar S2 wants 5 of the other 8).
REPOS: dict[str, str] = {
    "engine2040": r"C:\engine2040",
    "forge": r"C:\forge",
    "factory": r"C:\Users\me\Desktop\autonomous-factory",
    "fp-research": r"C:\Users\me\Desktop\fp-research",
    "marketing-studio": r"C:\Users\me\Desktop\marketing-studio",
}


def _installer():
    spec = importlib.util.spec_from_file_location(
        "install_fleet_skills", HERE / "install_fleet_skills.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["install_fleet_skills"] = mod
    spec.loader.exec_module(mod)
    return mod


def dest_of(repo_root: str) -> Path:
    return Path(repo_root) / ".opencode" / "skills"


def built_skills(inst, only: list[str] | None = None) -> list[str]:
    names = only or [n for n in inst.FLEET if (inst.SKILLS / n / "SKILL.md").is_file()]
    return names


def check_repo(inst, repo: str, skills: list[str]) -> list[str]:
    """Read-only empty-diff check for one repo. Writes nothing."""
    dest = dest_of(REPOS[repo])
    problems: list[str] = []
    for name in skills:
        for line in inst.stale(name, dest):
            problems.append(f"{name}: {line}")
    return problems


def prove_shape(inst, skills: list[str]) -> tuple[int, str]:
    """Install into a temp dir then check: the shape must show an empty diff."""
    with tempfile.TemporaryDirectory(prefix="g16-install5-") as tmp:
        dest = Path(tmp) / "installed"
        for name in skills:
            inst.install(name, dest)
        problems: list[str] = []
        for name in skills:
            for line in inst.stale(name, dest):
                problems.append(f"{name}: {line}")
        if problems:
            detail = "; ".join(problems[:5])
            return 1, f"RESULT STALE: shape left {len(problems)} diffs in temp dir ({detail})"
        return 0, f"RESULT CONVERGED: shape installs {len(skills)} skills then checks empty (dry run, nothing written)"


def inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repos", nargs="*", help="only these repos (default: all 5)")
    ap.add_argument("--skills", nargs="*", default=None, help="only these skills (default: built fleet)")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when any repo shows a diff (default: report only)")
    ap.add_argument("--apply", action="store_true",
                    help="converge --to for real (default is a dry run, nothing kept)")
    ap.add_argument("--to", default=None, help="destination dir (required with --apply)")
    args = ap.parse_args(argv)

    inst = _installer()
    names = built_skills(inst, args.skills)
    unknown_skills = [n for n in names if not (inst.SKILLS / n / "SKILL.md").is_file()]
    if unknown_skills or (args.skills and not names):
        print(f"not built here: {args.skills}")
        return 2
    repos = args.repos or sorted(REPOS)
    unknown_repos = [r for r in repos if r not in REPOS]
    if unknown_repos:
        print(f"unknown repo: {unknown_repos} (want one of {sorted(REPOS)})")
        return 2

    if args.apply:
        if not args.to:
            print("ERROR refused: --apply needs --to <dir> (dry run otherwise, nothing is written)")
            return 2
        dest = Path(args.to).resolve()
        if inside(dest, SKILLS_DIR.resolve()) or dest == SKILLS_DIR.resolve():
            print(f"ERROR refused: --to {dest} is inside skills/ (a nested output crashed the OpenCode server 9 times)")
            return 2
        for name in names:
            inst.install(name, dest)
        problems: list[str] = []
        for name in names:
            for line in inst.stale(name, dest):
                problems.append(f"{name}: {line}")
        for line in problems[:10]:
            print(f"STALE {line}")
        print(f"RESULT CONVERGED: {len(names)} skills to {dest}, empty diff" if not problems
              else f"RESULT STALE: {len(problems)} diffs remain in {dest}")
        return 0 if not problems else 1

    print("g16 install5: dry run to 5 repos, empty-diff check (offline, nothing written)")
    worst = 0
    for repo in repos:
        problems = check_repo(inst, repo, names)
        dest = dest_of(REPOS[repo])
        if problems:
            print(f"STALE {repo}: {len(problems)} diffs vs {dest} (dry run, nothing written)")
            for line in problems[:3]:
                print(f"  stale {line}")
            if args.check:
                worst = 1
        else:
            print(f"CONVERGED {repo}: {len(names)} skills match {dest}, empty diff (dry run, nothing written)")
    with tempfile.TemporaryDirectory(prefix="g16-install5-repos-") as tmp:
        for repo in repos:
            dest = Path(tmp) / repo
            for name in names:
                inst.install(name, dest)
            problems = []
            for name in names:
                problems += inst.stale(name, dest)
            if problems:
                print(f"STALE {repo} (temp shape): {len(problems)} diffs")
                worst = 1
            else:
                print(f"CONVERGED {repo} (temp shape): {len(names)} skills, empty diff (dry run, nothing written)")
    code, said = prove_shape(inst, names)
    print(said)
    if code != 0:
        return 1
    return worst


if __name__ == "__main__":
    sys.exit(main())
