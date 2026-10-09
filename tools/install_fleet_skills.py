"""Copy fleet skills out of this repo (the source) into a folder an agent reads skills from.

    python tools/install_fleet_skills.py --to <skills dir> [skill ...]          # copy, report what changed
    python tools/install_fleet_skills.py --to <skills dir> --check [skill ...]  # exit 1 when a copy is stale
    python tools/install_fleet_skills.py --to <skills dir> --dry-run [skill ...]  # preview what would change, write nothing

Where OpenCode 1.18 looks (read from its own code and `opencode debug skill`, 2026-10-03):
  <repo>/.opencode/skills/<name>/SKILL.md      one repo
  <home>/.config/opencode/skills/<name>/SKILL.md   every repo on the PC (global)
Never keep the same skill name in both places: OpenCode logs a duplicate and the later one wins.

A copy holds SKILL.md, references/*.md and the scripts the skill names. The test and proof files stay here.
With no skill names, every fleet skill that is built is copied.
"""
from __future__ import annotations

import argparse
import base64
import datetime
import difflib
import filecmp
import hashlib
import json
import shutil
import sys
from pathlib import Path

# STEAL S (J4) idea from twpayne/chezmoi (MIT): source-state kept in the repo,
# verify names each drifted file and diff shows the per-file change, apply converges it.
# Fresh port below (stale/file_diff/install): no chezmoi code copied.

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
FLEET = ["pwsh-for-bash-writers", "git-one-branch", "real-browser-automation", "bevy-rust-ecs", "engine-builder", "repo-read-first", "edit-reread", "edit-unique", "task-scope", "bash-abort-guard", "ready-file-check", "bash-allowlist", "bash-spawn-guard", "read-offset-guard", "cargo-book", "fetch-github-first", "playwright-docs", "edit-verify", "websearch-retry", "repomap-guard", "edit-identical", "keeper-ready", "read-abort-guard", "edit-abort-guard", "ripgrep-search", "axios-get", "octokit-request", "judge-score-risk", "repro-first", "batch-first", "brief-gate", "yq-jq", "gron-json", "write-abort-guard", "bat-cat", "delta-diff", "sd-replace", "github-file-guard", "hexyl-hex", "hyperfine-bench", "grep-overflow-guard", "lsd-ls", "vivid-colors", "pipe-run", "game-patterns-free"]
# Source-only files: the pair list and its checker, and the proof that the live tests passed.
SKIP_FILES = {"live-proof.json", "pairs.json", "run_pairs.py", "pairs_to_md.py"}
SKIP_DIRS = {"export", "__pycache__", ".pytest_cache"}
RECORD_FILENAME = ".install-record.json"


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


# STEAL S idea from lirantal/lockfile-lint (Apache-2.0, https://github.com/lirantal/lockfile-lint):
# installed set validated against the manifest, files outside it are refused.
# Fresh code below (outside_manifest): no lockfile-lint code copied.


def outside_manifest(name: str, dest_root: Path) -> list[str]:
    """Posix rel paths in the copy outside the payload manifest (extras fail the check)."""
    dest = dest_root / name
    if not dest.is_dir():
        return []
    want = {rel.as_posix() for rel in payload(name)}
    have = {p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file() and p.name != RECORD_FILENAME}
    return sorted(have - want)


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
    problems += [f"extra {rel}" for rel in outside_manifest(name, dest_root)]
    return problems


def file_diff(name: str, dest_root: Path, rel_posix: str, max_lines: int = 40) -> list[str]:
    """Unified diff lines for one changed file (fresh code; text with replace)."""
    try:
        a = (SKILLS / name / rel_posix).read_text(encoding="utf-8", errors="replace").splitlines()
        b = (dest_root / name / rel_posix).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    diff = list(difflib.unified_diff(a, b, fromfile=f"a/{rel_posix}", tofile=f"b/{rel_posix}", lineterm=""))
    return diff[:max_lines]

# STEAL M idea from dotdrift/dotdrift (MIT, https://github.com/dotdrift/dotdrift):
# 3-way drift via sha256 repo vs live vs record: repo-ahead when live matches record, live-drifted when repo matches record, conflict when both differ.
# Fresh code below, no donor code copied.
# STEAL S idea from tuck/tuck (Apache-2.0, https://github.com/tuck/tuck):
# typed check states with json flag, additive only, existing check output unchanged.
# Fresh code below, no donor code copied.
def _sha256_file(path: Path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None
def _record_path(name: str, dest_root: Path) -> Path:
    return dest_root / name / RECORD_FILENAME
def _load_record(name: str, dest_root: Path):
    try:
        doc = json.loads(_record_path(name, dest_root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return doc if isinstance(doc, dict) else {}
def _save_record(name: str, dest_root: Path) -> None:
    rec = {}
    for rel in payload(name):
        h = _sha256_file(SKILLS / name / rel)
        if h is not None:
            rec[rel.as_posix()] = h
    try:
        _record_path(name, dest_root).write_text(json.dumps(rec, indent=2, sort_keys=True) + chr(10), encoding="utf-8")
    except OSError:
        pass
def classify(name: str, dest_root: Path):
    states = []
    record = _load_record(name, dest_root)
    base = SKILLS / name
    dest = dest_root / name
    for rel in payload(name):
        posix = rel.as_posix()
        repo_h = _sha256_file(base / rel)
        live = dest / rel
        if not live.is_file():
            states.append({"file": posix, "state": "missing"})
            continue
        live_h = _sha256_file(live)
        if live_h == repo_h:
            continue
        rec_h = record.get(posix)
        if rec_h is None:
            states.append({"file": posix, "state": "changed"})
        elif live_h == rec_h:
            states.append({"file": posix, "state": "repo-ahead"})
        elif repo_h == rec_h:
            states.append({"file": posix, "state": "live-drifted"})
        else:
            states.append({"file": posix, "state": "conflict"})
    for rel in outside_manifest(name, dest_root):
        states.append({"file": rel, "state": "extra"})
    return states


# Ported from skillsgate/skillsgate (MIT, https://github.com/skillsgate/skillsgate)
# Donor shape apps/desktop/skills-lock.json: version 1 with skills map of name to source and computedHash-sha256
# Fresh port in this repo style: sha256 per skill payload, drift when hash differs or entry missing.
LOCK_VERSION = 1


def _hash_entry(data) -> str:
    """sha256 hex of a skill payload given as str or bytes."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def write_lock(path, entries) -> Path:
    """Write a versioned hash lock for entries map of name to payload."""
    lock = Path(path)
    lock.parent.mkdir(parents=True, exist_ok=True)
    skills = {}
    for name in sorted(entries):
        skills[name] = {"source": "fleet", "computedHash-sha256": _hash_entry(entries[name])}
    doc = {"version": LOCK_VERSION, "skills": skills}
    lock.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def lock_drift(path, entries) -> bool:
    """True when any payload hash differs or any entry is missing from the lock."""
    lock = Path(path)
    try:
        doc = json.loads(lock.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True
    if not isinstance(doc, dict):
        return True
    if doc.get("version") != LOCK_VERSION:
        return True
    skills = doc.get("skills")
    if not isinstance(skills, dict):
        return True
    for name in entries:
        entry = skills.get(name)
        if not isinstance(entry, dict):
            return True
        if entry.get("computedHash-sha256") != _hash_entry(entries[name]):
            return True
    return False



# STEAL S idea from extensiondev/artifact-integrity (Apache-2.0, https://github.com/extensiondev/artifact-integrity):
# pinned digest order expectedSha256 over manifest files.zip.sha256 over metadata sha256 or SRI, requireDigest fail-closed.
# Fresh code below, no donor code copied.
DIGEST_ORDER = ("expectedSha256", "files.zip.sha256", "sha256")


def _sri_sha256_to_hex(sri):
    """Hex digest from a sha256 SRI value or None when unparsable."""
    if not isinstance(sri, str):
        return None
    for token in sri.strip().split():
        if not token.startswith("sha256-"):
            continue
        raw = token[len("sha256-"):]
        if not raw:
            continue
        try:
            digest = base64.b64decode(raw, validate=True)
        except Exception:
            continue
        if len(digest) != 32:
            continue
        return digest.hex()
    return None


def pinned_digest(artifact):
    """Pinned hex digest in DIGEST_ORDER or (None, None) when absent."""
    if not isinstance(artifact, dict):
        return (None, None)
    expected = artifact.get("expectedSha256")
    if isinstance(expected, str) and expected.strip():
        return (DIGEST_ORDER[0], expected.strip().lower())
    manifest = artifact.get("manifest")
    if isinstance(manifest, dict):
        direct = manifest.get("files.zip.sha256")
        if isinstance(direct, str) and direct.strip():
            return (DIGEST_ORDER[1], direct.strip().lower())
        files = manifest.get("files")
        if isinstance(files, dict):
            zipped = files.get("zip")
            if isinstance(zipped, dict):
                nested = zipped.get("sha256")
                if isinstance(nested, str) and nested.strip():
                    return (DIGEST_ORDER[1], nested.strip().lower())
    metadata = artifact.get("metadata")
    if isinstance(metadata, dict):
        meta_hex = metadata.get("sha256")
        if isinstance(meta_hex, str) and meta_hex.strip():
            return (DIGEST_ORDER[2], meta_hex.strip().lower())
        integrity = metadata.get("integrity")
        parsed = _sri_sha256_to_hex(integrity) if isinstance(integrity, str) else None
        if parsed:
            return (DIGEST_ORDER[2], parsed)
    return (None, None)


def verify_artifact(artifact, actual_sha256, require_digest=True):
    """One item checks list with digest-present or digest-match finding."""
    source, expected = pinned_digest(artifact)
    if expected is None:
        ok = not require_digest
        return [
            {
                "id": "digest-present",
                "ok": ok,
                "level": "error" if require_digest else "info",
                "title": "Pinned digest is present",
                "summary": "No pinned digest found in expectedSha256, manifest files.zip.sha256, or metadata sha256 or SRI.",
                "remediation": "Pin expectedSha256 or manifest files.zip.sha256 or metadata sha256 before install.",
                "expected": None,
                "actual": actual_sha256,
            }
        ]
    actual_text = actual_sha256 if isinstance(actual_sha256, str) else ""
    ok = actual_text.strip().lower() == expected.lower() and bool(actual_text.strip())
    return [
        {
            "id": "digest-match",
            "ok": ok,
            "level": "info" if ok else "error",
            "title": "Pinned digest matches artifact bytes",
            "summary": "Pinned digest matches computed sha256." if ok else "Pinned digest does not match computed sha256.",
            "remediation": "No action needed." if ok else "Refuse install and repin from trusted source.",
            "expected": expected,
            "actual": actual_sha256,
        }
    ]


def unverified_install_paths(artifacts, require_digest=True):
    """Sorted artifact names with no pinned digest, empty when not required."""
    if not require_digest:
        return []
    names = []
    for artifact in artifacts or []:
        if not isinstance(artifact, dict):
            continue
        source, expected = pinned_digest(artifact)
        if expected is None:
            name = artifact.get("name")
            if isinstance(name, str) and name:
                names.append(name)
    return sorted(names)



# STEAL S idea from percymcn/agent-cookbook (MIT, https://github.com/percymcn/agent-cookbook/blob/67a791a/scripts/install_skill.py, LICENSE https://github.com/percymcn/agent-cookbook/blob/67a791a/LICENSE):
# timestamped backup-before-overwrite (.bak-%Y%m%d-%H%M%S copytree) + --dry-run preview install verb.
# Fresh code below (backup_installed/install dry-run): no donor code copied.


def backup_installed(name: str, dest_root: Path):
    dest = dest_root / name
    if not dest.is_dir():
        return None
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = dest_root / (name + '.bak-' + stamp)
    n = 1
    while backup.exists():
        n += 1
        backup = dest_root / (name + '.bak-' + stamp + '-' + str(n))
    shutil.copytree(dest, backup)
    return backup


def install(name: str, dest_root: Path, dry_run=False):
    base, dest = SKILLS / name, dest_root / name
    changes = stale(name, dest_root)
    if dry_run:
        return changes
    if changes and dest.is_dir():
        backup_installed(name, dest_root)
    for rel in payload(name):
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(base / rel, target)
    for line in changes:
        if line.startswith('extra '):
            (dest / line[6:]).unlink()
    _save_record(name, dest_root)
    return changes


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--to", required=True, help="skills folder to install into (its children are the skill folders)")
    ap.add_argument("--check", action="store_true", help="only compare; exit 1 when a copy is stale")
    ap.add_argument("--json", action="store_true", help="with --check print typed JSON states per file (missing, changed, extra, repo-ahead, live-drifted, conflict; ok when clean)")
    ap.add_argument('--dry-run', action='store_true', help='only preview; print what would change and write nothing')
    ap.add_argument("skills", nargs="*")
    args = ap.parse_args(argv)
    names = args.skills or [n for n in FLEET if (SKILLS / n / "SKILL.md").is_file()]
    unknown = [n for n in names if not (SKILLS / n / "SKILL.md").is_file()]
    if unknown:
        print(f"not built here: {unknown}")
        return 2
    if args.to == "global":
        dest_root = Path.home() / ".config" / "opencode" / "skills"
    else:
        dest_root = Path(args.to)
    worst = 0
    for name in names:
        if args.check:
            problems = stale(name, dest_root)
            print(f"{'STALE' if problems else 'ok   '} {name}: {'; '.join(problems) if problems else 'copy matches the source'}")
            for line in problems:
                if line.startswith("changed "):
                    for dl in file_diff(name, dest_root, line[8:]):
                        print(f"  diff {dl}")
            if args.json:
                print(json.dumps({"skill": name, "ok": not problems, "states": classify(name, dest_root)}, sort_keys=True))
            worst = 1 if problems else worst
        elif args.dry_run:
            problems = stale(name, dest_root)
            print(f"dry-run {name} -> {dest_root / name}: {'; '.join(problems) if problems else 'nothing to change'}")
        else:
            changes = install(name, dest_root)
            print(f"{'updated' if changes else 'current'} {name} -> {dest_root / name}: {'; '.join(changes) if changes else 'nothing to change'}")
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
