# Attribution: pattern steal from openclaw/clawhub@d044664
# packages/clawhub/src/skills.ts (MIT,
# https://github.com/openclaw/clawhub/blob/d044664a7636ec74b0092aa13fc0fcad1e660121/packages/clawhub/src/skills.ts):
# readLockfile/writeLockfile + lock.json
# (registry/slug/installedVersion/installedAt/fingerprint) + origin.json per
# skill, plus listManualSkills (installed-without-lock to locked). Fresh
# Python stdlib-only implementation; no donor code copied.
"""Install lockfile helper for MCP skill installs (stdlib only).

Port of the clawhub lock pattern (ideas only, no paste):

* lock.json at <workdir>/.clawhub/lock.json holds one entry per locked
  skill: registry / slug / installedVersion / installedAt / fingerprint.
* origin.json at <skill-dir>/.clawhub/origin.json holds the same entry
  for that one skill.
* Skills installed on disk without a lock entry (manual / installed-without-
  lock) are moved to locked by adopt_installed_without_lock.

Layout note: workdir is the project root (donor workdir); the skills
live in <workdir>/skills/<slug> (or any skills_dir you pass). The lock
lives one level above the skills, the origin lives inside each skill folder.
workdir may also equal skills_dir for single-dir setups; both work
because paths are derived explicitly.

Stdlib only: hashlib + json + time + pathlib + os.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Iterable, Mapping

DOT_DIR = ".clawhub"
LEGACY_DOT_DIR = ".clawdhub"
LOCK_FILENAME = "lock.json"
ORIGIN_FILENAME = "origin.json"
LOCK_VERSION = 1

__all__ = [
    "DOT_DIR",
    "LEGACY_DOT_DIR",
    "LOCK_FILENAME",
    "ORIGIN_FILENAME",
    "LOCK_VERSION",
    "sha256_hex",
    "build_fingerprint",
    "hash_skill_files",
    "fingerprint_skill",
    "skill_version",
    "read_lockfile",
    "write_lockfile",
    "read_skill_origin",
    "write_skill_origin",
    "make_origin",
    "record_install",
    "locked_slugs",
    "list_manual_skills",
    "adopt_installed_without_lock",
    "ensure_locked_skills",
]


def _as_path(value: str | Path) -> Path:
    return value if isinstance(value, Path) else Path(value)


def _is_valid_slug(slug: Any) -> bool:
    if not isinstance(slug, str) or not slug:
        return False
    if slug.startswith("."):
        return False
    if "/" in slug or "\\" in slug or ".." in slug:
        return False
    if "\x00" in slug or "\n" in slug or "\r" in slug:
        return False
    return True


def _is_finite_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float)) and value == value and value not in (float("inf"), float("-inf"))


def sha256_hex(data: bytes) -> str:
    """Hex sha256 of bytes."""
    return hashlib.sha256(data).hexdigest()


def build_fingerprint(files: Iterable[Mapping[str, Any]]) -> str:
    """Donor buildSkillFingerprint: sha256 over sorted path:sha256 lines.

    Entries missing a truthy path/sha256 are skipped, the rest sort by
    path and join with newline before the final sha256.
    """
    pairs: list[tuple[str, str]] = []
    for entry in files:
        try:
            path = entry["path"]
            digest = entry["sha256"]
        except (KeyError, TypeError):
            continue
        if not path or not digest:
            continue
        pairs.append((str(path), str(digest)))
    pairs.sort(key=lambda item: item[0])
    payload = "\n".join(f"{path}:{digest}" for path, digest in pairs)
    return sha256_hex(payload.encode("utf-8"))


def _is_skipped_rel(rel: str) -> bool:
    """True when a slash-joined relative path stays out of the fingerprint.

    Donor skips any dot path segment plus node_modules; we also skip
    __pycache__ bytecode noise and a top-level export copy (generated output
    must never move the pin).
    """
    parts = rel.split("/")
    for seg in parts:
        if not seg:
            return True
        if seg.startswith("."):
            return True
    if "node_modules" in parts or "__pycache__" in parts:
        return True
    if parts[0] == "export":
        return True
    return False


def hash_skill_files(skill_dir: str | Path) -> dict:
    """Hash every content file under skill_dir; return files plus fingerprint.

    Mirrors donor hashSkillFiles: per-file sha256 plus the bundle
    fingerprint from build_fingerprint. Dot dirs, node_modules,
    __pycache__ and top-level export are excluded.
    """
    base = _as_path(skill_dir)
    hashed: list[dict] = []
    if not base.is_dir():
        return {"files": hashed, "fingerprint": build_fingerprint([])}
    for here, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        keep: list[str] = []
        for d in dirs:
            if d == "node_modules" or d == "__pycache__":
                continue
            if d == "export" and Path(here) == base:
                continue
            keep.append(d)
        dirs[:] = keep
        for name in files:
            if name.startswith("."):
                continue
            abs_path = Path(here) / name
            try:
                rel = abs_path.relative_to(base).as_posix()
            except ValueError:
                continue
            if _is_skipped_rel(rel):
                continue
            try:
                data = abs_path.read_bytes()
            except OSError:
                continue
            hashed.append({"path": rel, "sha256": sha256_hex(data), "size": len(data)})
    hashed.sort(key=lambda item: item["path"])
    return {"files": hashed, "fingerprint": build_fingerprint(hashed)}


def fingerprint_skill(skill_dir: str | Path) -> str:
    """Bundle fingerprint for one installed skill folder."""
    return str(hash_skill_files(skill_dir).get("fingerprint", sha256_hex(b"")))


def _parse_frontmatter_version(text: str) -> str:
    """Read version from a SKILL.md frontmatter block; default 0.1.0."""
    if not isinstance(text, str) or not text.startswith("---"):
        return "0.1.0"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "0.1.0"
    for line in parts[1].splitlines():
        stripped = line.strip()
        if stripped.startswith("version:"):
            value = stripped.split(":", 1)[1].strip()
            value = value.strip(chr(34)).strip(chr(39)).strip()
            if value:
                return value
    return "0.1.0"


def skill_version(skill_dir: str | Path) -> str:
    """Installed version from SKILL.md frontmatter; 0.1.0 when missing."""
    try:
        text = (_as_path(skill_dir) / "SKILL.md").read_text(encoding="utf-8")
    except OSError:
        return "0.1.0"
    return _parse_frontmatter_version(text)


def _lock_paths(workdir: str | Path) -> list[Path]:
    base = _as_path(workdir)
    return [base / DOT_DIR / LOCK_FILENAME, base / LEGACY_DOT_DIR / LOCK_FILENAME]


def _origin_paths(skill_dir: str | Path) -> list[Path]:
    base = _as_path(skill_dir)
    return [base / DOT_DIR / ORIGIN_FILENAME, base / LEGACY_DOT_DIR / ORIGIN_FILENAME]


def _clean_origin(value: Any) -> dict | None:
    """Validate one origin or lock entry; return cleaned dict or None."""
    if not isinstance(value, dict):
        return None
    if value.get("version") != LOCK_VERSION:
        return None
    registry = value.get("registry")
    slug = value.get("slug")
    installed_version = value.get("installedVersion")
    installed_at = value.get("installedAt")
    if not isinstance(registry, str) or not registry.strip():
        return None
    if not _is_valid_slug(slug):
        return None
    if not isinstance(installed_version, str) or not installed_version.strip():
        return None
    if not _is_finite_number(installed_at):
        return None
    cleaned: dict[str, Any] = {
        "version": LOCK_VERSION,
        "registry": registry,
        "slug": slug,
        "installedVersion": installed_version,
        "installedAt": installed_at,
    }
    fingerprint = value.get("fingerprint")
    if isinstance(fingerprint, str) and fingerprint:
        cleaned["fingerprint"] = fingerprint
    for key in ("ownerHandle", "sourceRef", "sourceRepository", "sourcePath", "sourceUrl", "canonicalRef", "trustLabel", "artifactIdentity"):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate:
            cleaned[key] = candidate
    if value.get("sourceKind") == "skills-sh":
        cleaned["sourceKind"] = "skills-sh"
    if value.get("clawhubScan") in ("unscanned", "scanned"):
        cleaned["clawhubScan"] = value["clawhubScan"]
    return cleaned


def read_lockfile(workdir: str | Path) -> dict:
    """Donor readLockfile: parsed lock or empty default with version 1.

    Tries dot lock then legacy dot lock. Missing, corrupt or wrong-shaped
    files fall through to the empty default; valid entries inside a
    readable file are kept, invalid ones dropped.
    """
    for path in _lock_paths(workdir):
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(parsed, dict):
            continue
        if parsed.get("version") != LOCK_VERSION:
            continue
        skills = parsed.get("skills")
        if not isinstance(skills, dict):
            continue
        kept: dict[str, dict] = {}
        for slug, entry in skills.items():
            cleaned = _clean_origin(entry)
            if cleaned is None:
                continue
            if cleaned["slug"] != slug:
                continue
            kept[slug] = cleaned
        return {"version": LOCK_VERSION, "skills": kept}
    return {"version": LOCK_VERSION, "skills": {}}


def write_lockfile(workdir: str | Path, lock: Mapping[str, Any]) -> Path:
    """Donor writeLockfile: write dot lock.json under workdir."""
    base = _as_path(workdir)
    skills = lock.get("skills") if isinstance(lock, Mapping) else None
    if not isinstance(skills, dict):
        raise ValueError("lock needs a skills dict")
    cleaned: dict[str, dict] = {}
    for slug, entry in skills.items():
        item = _clean_origin(entry)
        if item is None or item["slug"] != slug:
            raise ValueError(f"invalid lock entry for {slug!r}")
        cleaned[slug] = item
    out = base / DOT_DIR / LOCK_FILENAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"version": LOCK_VERSION, "skills": cleaned}, indent=2) + "\n", encoding="utf-8")
    return out


def read_skill_origin(skill_dir: str | Path) -> dict | None:
    """Donor readSkillOrigin: validated origin dict or None."""
    for path in _origin_paths(skill_dir):
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        cleaned = _clean_origin(parsed)
        if cleaned is None:
            return None
        return cleaned
    return None


def write_skill_origin(skill_dir: str | Path, origin: Mapping[str, Any]) -> Path:
    """Donor writeSkillOrigin: write <skill>/.clawhub/origin.json."""
    cleaned = _clean_origin(dict(origin))
    if cleaned is None:
        raise ValueError("invalid origin (need version 1 plus registry/slug/installedVersion/installedAt)")
    base = _as_path(skill_dir)
    if base.name != cleaned["slug"]:
        raise ValueError("origin slug must match folder name")
    out = base / DOT_DIR / ORIGIN_FILENAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cleaned, indent=2) + "\n", encoding="utf-8")
    return out


def make_origin(registry: str, slug: str, installed_version: str, fingerprint: str | None = None, installed_at: int | float | None = None, **extra: Any) -> dict:
    """Build one lock/origin entry (validated on write, not here)."""
    if installed_at is None:
        installed_at = int(time.time() * 1000)
    entry: dict[str, Any] = {
        "version": LOCK_VERSION,
        "registry": registry,
        "slug": slug,
        "installedVersion": installed_version,
        "installedAt": installed_at,
    }
    if fingerprint:
        entry["fingerprint"] = fingerprint
    entry.update(extra)
    cleaned = _clean_origin(entry)
    if cleaned is None:
        raise ValueError("invalid origin fields")
    return cleaned


def record_install(workdir: str | Path, skill_dir: str | Path, registry: str, slug: str, installed_version: str, fingerprint: str | None = None, installed_at: int | float | None = None, **extra: Any) -> dict:
    """Record one install: refresh origin.json, upsert the lock.json entry."""
    skill_path = _as_path(skill_dir)
    if fingerprint is None:
        try:
            fingerprint = fingerprint_skill(skill_path)
        except OSError:
            fingerprint = None
    origin = make_origin(registry, slug, installed_version, fingerprint=fingerprint, installed_at=installed_at, **extra)
    write_skill_origin(skill_path, origin)
    lock = read_lockfile(workdir)
    lock["skills"][slug] = origin
    write_lockfile(workdir, lock)
    return origin


def locked_slugs(lock: Mapping[str, Any]) -> set[str]:
    """Slug set locked in a lock dict."""
    skills = lock.get("skills") if isinstance(lock, Mapping) else None
    if not isinstance(skills, dict):
        return set()
    return set(skills)


def list_manual_skills(skills_dir: str | Path, locked: Iterable[str] | Mapping[str, Any]) -> list[str]:
    """Donor listManualSkills: installed folders missing from the lock.

    A folder counts as installed when it holds SKILL.md or a readable
    origin.json (donor hasSkillMetadata). Dot folders never count.
    """
    base = _as_path(skills_dir)
    if isinstance(locked, Mapping):
        if "skills" in locked and isinstance(locked.get("skills"), dict):
            locked_set = set(locked["skills"])
        elif "version" in locked:
            locked_set = set()
        else:
            locked_set = set(locked)
    else:
        locked_set = set(locked)
    manual: list[str] = []
    try:
        entries = list(base.iterdir())
    except OSError:
        return manual
    for entry in entries:
        if not entry.is_dir():
            continue
        name = entry.name
        if name.startswith("."):
            continue
        if name in locked_set:
            continue
        has_skill = (entry / "SKILL.md").is_file()
        has_origin = read_skill_origin(entry) is not None
        if has_skill or has_origin:
            manual.append(name)
            continue
        raw_origin = any(p.exists() for p in _origin_paths(entry))
        if raw_origin:
            manual.append(name)
    manual.sort()
    return manual


def adopt_installed_without_lock(skills_dir: str | Path, workdir: str | Path | None = None, registry: str = "local", now: int | float | None = None) -> list[str]:
    """Move installed-without-lock skills into the lockfile; return adopted slugs.

    For each manual skill (on disk, not in lock.json): keep its existing
    valid origin.json when the slug matches (filling a missing fingerprint
    from disk), else mint a fresh origin from SKILL.md version plus
    fingerprint. Every adopted skill ends with both an origin.json and a
    lock.json entry. Idempotent: a second call adopts nothing.
    """
    skills_base = _as_path(skills_dir)
    work_base = _as_path(workdir) if workdir is not None else skills_base.parent
    if now is None:
        now = int(time.time() * 1000)
    lock = read_lockfile(work_base)
    manual = list_manual_skills(skills_base, locked_slugs(lock))
    adopted: list[str] = []
    for slug in manual:
        if not _is_valid_slug(slug):
            continue
        skill_path = skills_base / slug
        existing = read_skill_origin(skill_path)
        if existing is not None and existing.get("slug") == slug:
            if not existing.get("fingerprint"):
                try:
                    existing["fingerprint"] = fingerprint_skill(skill_path)
                except OSError:
                    pass
            origin = existing
            try:
                write_skill_origin(skill_path, origin)
            except (OSError, ValueError):
                continue
        else:
            version = skill_version(skill_path)
            try:
                fingerprint = fingerprint_skill(skill_path)
            except OSError:
                fingerprint = sha256_hex(b"")
            try:
                origin = make_origin(registry, slug, version, fingerprint=fingerprint, installed_at=now)
            except ValueError:
                continue
            try:
                write_skill_origin(skill_path, origin)
            except (OSError, ValueError):
                continue
        lock["skills"][slug] = origin
        adopted.append(slug)
    if adopted:
        write_lockfile(work_base, lock)
    return sorted(adopted)


def ensure_locked_skills(skills_dir: str | Path, workdir: str | Path | None = None, registry: str = "local", now: int | float | None = None) -> list[str]:
    """Alias of adopt_installed_without_lock for install-call sites."""
    return adopt_installed_without_lock(skills_dir, workdir=workdir, registry=registry, now=now)
