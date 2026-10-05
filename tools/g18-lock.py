"""G-18 lockfile plus converge proof (TS-7 registry row, R3).

Own original work (stdlib only). Builds on the TS-7 shapes from
tools/skill_registry.py without changing them: freeze writes the manifest,
this tool writes the lock, converge proves manifest vs lock vs registry
agree on one immutable version per skill.

MCP versioning rule (X-18 scout): versions are immutable and exact.
Range strings are rejected: ^ ~ >= <= > < * x | ||, spaces, or partial
numbers like "1.2". Only N.N.N pins pass.

Commands (all offline, no network):

    python tools/g18-lock.py lock --skills skills --out <lock.json> [name ...]
    python tools/g18-lock.py converge --manifest <m> --lock <l> --registry <r> --skills skills
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKILLS = ROOT / "skills"

EXACT = re.compile(r"^\d+\.\d+\.\d+$")
RANGE_HINT = re.compile(r"[\^~*|<>\s]|x|X|\|\||\.\.|-")


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


def is_exact(version: str) -> bool:
    return bool(EXACT.match(str(version).strip()))


def is_range(version: str) -> bool:
    v = str(version).strip()
    if not v:
        return True
    if EXACT.match(v):
        return False
    return True


def parse_frontmatter(text: str) -> dict:
    meta = {"name": "", "description": "", "version": "", "license": ""}
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


SKIP_FILES = {"live-proof.json", "pairs.json", "run_pairs.py", "pairs_to_md.py"}
SKIP_DIRS = {"export", "__pycache__", ".pytest_cache"}


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


def cmd_lock(args) -> int:
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
    entries: dict = {}
    for name in names:
        fm = parse_frontmatter((skills_dir / name / "SKILL.md").read_text(encoding="utf-8"))
        ver = fm["version"]
        if not ver:
            print(f"FAIL {name}: version missing (immutable pin required)")
            return 2
        if is_range(ver):
            print(f"FAIL {name}: range version rejected: {ver!r} (use exact N.N.N)")
            return 2
        files = payload_files(skills_dir, name)
        entries[name] = {
            "version": ver,
            "skill_sha256": sha256_file(skills_dir / name / "SKILL.md"),
            "files": {rel: sha256_file(skills_dir / name / rel) for rel in files},
        }
    lock = {"generated_at": now, "source_pin": pin, "skills": entries}
    Path(args.out).write_text(json.dumps(lock, indent=2), encoding="utf-8")
    nfiles = sum(len(v["files"]) for v in entries.values())
    print(f"locked {len(names)} skills {nfiles} files pin {pin[:12]} -> {args.out}")
    return 0


def _as_versions(manifest: dict) -> dict:
    """Manifest skills may be a list (TS-7 freeze) or a dict; return name->version."""
    raw = manifest.get("skills", [])
    if isinstance(raw, dict):
        out = {}
        for name, entry in raw.items():
            out[name] = entry.get("version", "") if isinstance(entry, dict) else str(entry)
        return out
    out = {}
    for e in raw:
        if isinstance(e, dict) and e.get("name"):
            out[str(e["name"])] = str(e.get("version", ""))
    return out


def _as_registry(registry: dict) -> dict:
    out = {}
    for e in registry.get("skills", []):
        if isinstance(e, dict) and e.get("name"):
            out[str(e["name"])] = e
    return out


def cmd_converge(args) -> int:
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        lock = json.loads(Path(args.lock).read_text(encoding="utf-8"))
        registry = json.loads(Path(args.registry).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"ERROR cannot read input: {exc}")
        return 2
    skills_dir = Path(args.skills)
    problems: list[str] = []
    mvers = _as_versions(manifest)
    lskills = lock.get("skills", {}) if isinstance(lock.get("skills"), dict) else {}
    rentries = _as_registry(registry)
    names = sorted(set(mvers) | set(lskills) | set(rentries))
    if not names:
        print("RESULT FAIL: no skills in manifest, lock, or registry")
        return 1
    for name in names:
        mv, le, re_ = mvers.get(name), lskills.get(name), rentries.get(name)
        if mv is None:
            problems.append(f"{name}: missing from manifest")
            continue
        if le is None:
            problems.append(f"{name}: missing from lock")
            continue
        if re_ is None:
            problems.append(f"{name}: missing from registry")
            continue
        lv = le.get("version", "") if isinstance(le, dict) else ""
        rv = str(re_.get("version", ""))
        for label, ver in (("manifest", mv), ("lock", lv), ("registry", rv)):
            if not ver:
                problems.append(f"{name}: {label} version missing")
            elif is_range(str(ver)):
                problems.append(f"{name}: {label} range version rejected: {ver!r}")
        if mv != lv or mv != rv:
            problems.append(f"{name}: version drift manifest={mv!r} lock={lv!r} registry={rv!r}")
        try:
            rate = float(re_.get("eval_rate", -1))
            if not 0.0 <= rate <= 1.0:
                raise ValueError
        except (TypeError, ValueError):
            problems.append(f"{name}: registry eval_rate not in 0..1")
        if skills_dir.is_dir() and isinstance(le, dict):
            want = le.get("files", {})
            d_skill = skills_dir / name
            for rel, sha in sorted(want.items()):
                t = d_skill / rel
                if not t.is_file():
                    problems.append(f"{name}: missing file {rel}")
                elif sha256_file(t) != sha:
                    problems.append(f"{name}: changed file {rel}")
    for line in problems:
        print(f"STALE {line}")
    pin = str(lock.get("source_pin") or manifest.get("source_pin") or registry.get("source_pin") or "")[:12]
    if problems:
        print(f"RESULT STALE: {len(problems)} diffs, {len(names)} skills, pin {pin}")
        return 1
    print(f"RESULT CONVERGED: {len(names)} skills, versions pinned, hashes match, pin {pin}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    lk = sub.add_parser("lock", help="write a lockfile (skill, immutable version, hash)")
    lk.add_argument("--skills", default=str(DEFAULT_SKILLS))
    lk.add_argument("--out", required=True)
    lk.add_argument("skills_only", nargs="*")
    lk.set_defaults(fn=cmd_lock)
    cv = sub.add_parser("converge", help="prove manifest vs lock vs registry agree")
    cv.add_argument("--manifest", required=True)
    cv.add_argument("--lock", required=True)
    cv.add_argument("--registry", required=True)
    cv.add_argument("--skills", default=str(DEFAULT_SKILLS))
    cv.set_defaults(fn=cmd_converge)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
