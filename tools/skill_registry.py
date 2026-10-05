"""Pinned skill installer: manifest plus lock plus registry index (TS-7, R3).

Own original work (stdlib only): no donor code copied. Shape ideas from the
standard package-manager manifest/lock split are generic; the payload skip set
mirrors tools/install_fleet_skills.py (own fleet) so a lock install converges
to the same copy the fleet installer makes.

Commands (all offline, no network)::

    python tools/skill_registry.py freeze --skills skills --manifest <f> --lock <f> [name ...]
    python tools/skill_registry.py install --lock <f> --source skills --to <dir> [--check] [name ...]
    python tools/skill_registry.py registry --skills skills --out <f> [name ...]
    python tools/skill_registry.py validate --registry <f> --skills skills

freeze writes a manifest (skills with versions) and a lock (per-file sha256
plus a source pin: the repo HEAD sha, else "worktree"). install converges a
destination dir from the lock (copies missing/changed, removes extra) and
--check exits 1 on any diff. registry writes registry.json (eval_rate plus
source pin per skill); validate checks it (names, versions, eval_rate range,
source pin, SKILL.md present) and exits 1 on failure.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKILLS = ROOT / "skills"
EVAL_GATE = 0.6

SKIP_FILES = {"live-proof.json", "pairs.json", "run_pairs.py", "pairs_to_md.py"}
SKIP_DIRS = {"export", "__pycache__", ".pytest_cache"}


def _utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def source_pin() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                           capture_output=True, text=True, timeout=30)
        sha = r.stdout.strip()
        if r.returncode == 0 and len(sha) >= 7:
            return sha
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    return "worktree"


def parse_frontmatter(text: str) -> dict:
    meta = {"name": "", "description": "", "version": "0.1.0",
            "author": "skillworks", "license": ""}
    if not text.startswith("---"):
        return meta
    parts = text.split("---", 2)
    if len(parts) < 3:
        return meta
    for line in parts[1].splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key, val = key.strip(), val.strip()
        if key in meta and val:
            meta[key] = val
    return meta


def skill_names(skills_dir: Path, only: list[str] | None = None) -> list[str]:
    if only:
        return [n for n in only if (skills_dir / n / "SKILL.md").is_file()]
    return sorted(p.name for p in skills_dir.iterdir()
                  if p.is_dir() and (p / "SKILL.md").is_file()
                  and p.name != "_template")


def payload_files(skills_dir: Path, name: str) -> list[str]:
    base = skills_dir / name
    out = []
    for p in sorted(base.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(base)
        if p.name in SKIP_FILES or SKIP_DIRS & set(rel.parts):
            continue
        out.append(rel.as_posix())
    return out


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def eval_rate(skills_dir: Path, name: str) -> tuple[float, int]:
    try:
        rep = json.loads((skills_dir / name / "eval_report.json").read_text(encoding="utf-8"))
        return float(rep.get("rate", 0.0)), int(rep.get("passed", 0))
    except (OSError, ValueError, TypeError, AttributeError):
        return 0.0, 0


def cmd_freeze(args) -> int:
    skills_dir = Path(args.skills)
    if not skills_dir.is_dir():
        print(f"ERROR skills dir missing: {skills_dir}")
        return 2
    names = skill_names(skills_dir, args.skills_only or None)
    unknown = [n for n in (args.skills_only or []) if not (skills_dir / n / "SKILL.md").is_file()]
    if unknown:
        print(f"not built here: {unknown}")
        return 2
    pin = source_pin()
    now = _utcnow()
    manifest_skills, lock_skills = [], {}
    for name in names:
        fm = parse_frontmatter((skills_dir / name / "SKILL.md").read_text(encoding="utf-8"))
        files = payload_files(skills_dir, name)
        file_shas = {rel: sha256_file(skills_dir / name / rel) for rel in files}
        manifest_skills.append({"name": fm["name"] or name, "version": fm["version"],
                                "description": fm["description"], "license": fm["license"],
                                "files": len(files)})
        lock_skills[name] = {"version": fm["version"], "files": file_shas}
    manifest = {"generated_at": now, "source_pin": pin, "skills": manifest_skills}
    lock = {"generated_at": now, "source_pin": pin, "skills": lock_skills}
    Path(args.manifest).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    Path(args.lock).write_text(json.dumps(lock, indent=2), encoding="utf-8")
    nfiles = sum(len(v["files"]) for v in lock_skills.values())
    print(f"froze {len(names)} skills {nfiles} files pin {pin[:12]} -> {args.manifest} + {args.lock}")
    return 0


def lock_diff(skills_dir: Path, lock: dict, dest: Path, names: list[str]) -> list[str]:
    problems: list[str] = []
    for name in names:
        entry = lock["skills"].get(name)
        if entry is None:
            problems.append(f"{name}: not in lock")
            continue
        want = entry.get("files", {})
        d = dest / name
        for rel, sha in sorted(want.items()):
            t = d / rel
            if not t.is_file():
                problems.append(f"{name}: missing {rel}")
            elif sha256_file(t) != sha:
                problems.append(f"{name}: changed {rel}")
        if d.is_dir():
            have = {p.relative_to(d).as_posix() for p in d.rglob("*") if p.is_file()}
            for rel in sorted(have - set(want)):
                problems.append(f"{name}: extra {rel}")
        src_skill = skills_dir / name
        if not src_skill.is_dir():
            problems.append(f"{name}: source missing")
    return problems


def cmd_install(args) -> int:
    lock_path = Path(args.lock)
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"ERROR cannot read lock {lock_path}: {exc}")
        return 2
    skills_dir = Path(args.source)
    dest = Path(args.to)
    names = args.skills_only or sorted(lock.get("skills", {}))
    unknown = [n for n in names if n not in lock.get("skills", {})]
    if unknown:
        print(f"not in lock: {unknown}")
        return 2
    problems = lock_diff(skills_dir, lock, dest, names)
    if args.check:
        for line in problems:
            print(f"STALE {line}")
        if problems:
            print(f"RESULT STALE: {len(problems)} diffs, lock pin {str(lock.get('source_pin'))[:12]}")
            return 1
        print(f"RESULT CONVERGED: {len(names)} skills from lock pin {str(lock.get('source_pin'))[:12]}, empty diff")
        return 0
    for name in names:
        want = lock["skills"][name].get("files", {})
        d = dest / name
        for rel in want:
            src = skills_dir / name / rel
            tgt = d / rel
            tgt.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, tgt)
        if d.is_dir():
            for p in d.rglob("*"):
                if p.is_file() and p.relative_to(d).as_posix() not in want:
                    p.unlink()
    problems = lock_diff(skills_dir, lock, dest, names)
    if problems:
        for line in problems:
            print(f"STALE {line}")
        print(f"RESULT STALE: {len(problems)} diffs remain")
        return 1
    print(f"RESULT CONVERGED: {len(names)} skills from lock pin {str(lock.get('source_pin'))[:12]}, empty diff")
    return 0


def cmd_registry(args) -> int:
    skills_dir = Path(args.skills)
    if not skills_dir.is_dir():
        print(f"ERROR skills dir missing: {skills_dir}")
        return 2
    names = skill_names(skills_dir, args.skills_only or None)
    pin = source_pin()
    now = _utcnow()
    entries = []
    for name in names:
        fm = parse_frontmatter((skills_dir / name / "SKILL.md").read_text(encoding="utf-8"))
        rate, passed = eval_rate(skills_dir, name)
        files = payload_files(skills_dir, name)
        skill_sha = sha256_file(skills_dir / name / "SKILL.md")
        entries.append({"name": name, "version": fm["version"], "description": fm["description"],
                        "license": fm["license"], "eval_rate": rate, "eval_passed": passed,
                        "above_gate": rate >= EVAL_GATE, "source_pin": pin,
                        "files": len(files), "skill_sha256": skill_sha})
    reg = {"generated_at": now, "source_pin": pin, "skills": entries}
    Path(args.out).write_text(json.dumps(reg, indent=2), encoding="utf-8")
    print(f"registry {len(entries)} skills pin {pin[:12]} -> {args.out}")
    return 0


def cmd_validate(args) -> int:
    try:
        reg = json.loads(Path(args.registry).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"ERROR cannot read registry {args.registry}: {exc}")
        return 2
    skills_dir = Path(args.skills)
    pin = str(reg.get("source_pin", ""))
    ok, fails = True, []
    seen: set[str] = set()
    for e in reg.get("skills", []):
        name = str(e.get("name", ""))
        if not name or name in seen:
            fails.append(f"{name or '?'}: duplicate or empty name")
            ok = False
            continue
        seen.add(name)
        if not (skills_dir / name / "SKILL.md").is_file():
            fails.append(f"{name}: SKILL.md missing")
            ok = False
        if not str(e.get("version", "")):
            fails.append(f"{name}: version missing")
            ok = False
        try:
            rate = float(e.get("eval_rate", -1))
            if not 0.0 <= rate <= 1.0:
                raise ValueError
        except (TypeError, ValueError):
            fails.append(f"{name}: eval_rate not in 0..1")
            ok = False
        if not str(e.get("source_pin", "")):
            fails.append(f"{name}: source_pin missing")
            ok = False
        sha = str(e.get("skill_sha256", ""))
        if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            fails.append(f"{name}: skill_sha256 not hex64")
            ok = False
    if not pin:
        fails.append("registry: source_pin missing")
        ok = False
    for line in fails:
        print(f"FAIL {line}")
    if ok:
        print(f"RESULT PASS: registry {len(seen)} skills pin {pin[:12]} validates")
        return 0
    print(f"RESULT FAIL: {len(fails)} registry problems")
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze", help="write manifest + lock from a skills dir")
    f.add_argument("--skills", default=str(DEFAULT_SKILLS))
    f.add_argument("--manifest", required=True)
    f.add_argument("--lock", required=True)
    f.add_argument("skills_only", nargs="*")
    f.set_defaults(fn=cmd_freeze)
    i = sub.add_parser("install", help="converge a dir from a lock (--check exits 1 on diff)")
    i.add_argument("--lock", required=True)
    i.add_argument("--source", default=str(DEFAULT_SKILLS))
    i.add_argument("--to", required=True)
    i.add_argument("--check", action="store_true")
    i.add_argument("skills_only", nargs="*")
    i.set_defaults(fn=cmd_install)
    r = sub.add_parser("registry", help="write registry.json index with eval rates")
    r.add_argument("--skills", default=str(DEFAULT_SKILLS))
    r.add_argument("--out", required=True)
    r.add_argument("skills_only", nargs="*")
    r.set_defaults(fn=cmd_registry)
    v = sub.add_parser("validate", help="validate a registry.json file")
    v.add_argument("--registry", required=True)
    v.add_argument("--skills", default=str(DEFAULT_SKILLS))
    v.set_defaults(fn=cmd_validate)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
